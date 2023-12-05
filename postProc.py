import openmc
import numpy as np
import tallierizer
import pickle

with openmc.StatePoint('statepoint.5.h5') as sp:
    heatingMeshTally = sp.get_tally(name = "Cartesian Mesh Heating Tally")
    neutronMeshTally = sp.get_tally(name = 'Cartesian Mesh Neutron Flux Tally')
    fwDPATally = sp.get_tally(name="FW DPA Tally")
    fwHeatingTally = sp.get_tally(name='FW Heating Tally')
    fwDPAmeshTally = sp.get_tally(name="FW DPA Mesh Tally")
    fwHeatingMeshTally = sp.get_tally(name="FW Heating Mesh Tally")
    breederTBRTally = sp.get_tally(name = "Breeder TBR Tally")
    breederHeatingTally = sp.get_tally(name= "Breeder Heating Tally")
    breederUmeshTBRTally = sp.get_tally(name="Breeder Mesh TBR Tally")
    breederUmeshHeatingTally = sp.get_tally(name = "Breeder Mesh Heating Tally")
    meshes = sp._meshes

print(meshes)
#some constants
mats = openmc.Materials.from_xml('materials.xml')
fwMat = mats[11] #FNSFFWstruct
fwVol = 15909811.971955 #cm3 from cubit
breederVol = 124350001.520557 #cm3 from cubit
power = 211e6 #W, should average 1 MW/m2 based on interior fw surface area
energyPerFusion = 17.6e6 #eV
eVtoJ = 1.60218e-19 #J/eV
neutronsPerSecond = power/(energyPerFusion*eVtoJ)
print("Power, MW: ", power/1e6)


#calculate DPA through entire FW
DPAfw, DPAstdevFw, = tallierizer.calcDPAIron(power, fwMat, fwVol, dpaTally=fwDPATally)

print("Average DPA in first wall layer: ", DPAfw)
print("Std Dev: ", DPAstdevFw)

#calculate DPA in FW mesh
fwMesh = meshes[3]
mean = fwDPAmeshTally.get_reshaped_data(value="mean")
stddev = fwDPAmeshTally.get_reshaped_data(value="std_dev")
volumes = fwMesh.volumes.T.flatten()

meshDPAfw, meshDPAstdevFw = tallierizer.calcDPAIron(power, fwMat, volumes, fwDPAmeshTally, mean = mean, stddev=stddev)

print("Average DPA in FW Mesh: ", np.average(meshDPAfw))
print("Std Dev: ", np.std(meshDPAfw)) #not sure this is correct
print("Max DPA in mesh: ", np.max(meshDPAfw))

fwMesh.write_data_to_vtk(
    filename = "fwMesh.vtk",
    datasets = {
        "Mean DPA per FPY": meshDPAfw,
        "DPA Std dev": meshDPAstdevFw
    },
    volume_normalization = False
)


#calculate heating in cartesian mesh
cylindricalMesh = meshes[2]
cylindricalVolumes = cylindricalMesh.volumes
mean = heatingMeshTally.get_reshaped_data(value='mean')
stddev = heatingMeshTally.get_reshaped_data(value='std_dev')
heatingMean = mean[:,0,0] #eV/source particle
heatingStddev = stddev[:,0,0] #ev/source particle
cylindricalMeshHeatingMean, cylindricalMeshHeatingStddev = tallierizer.calcHeating(heatingMean, heatingStddev, power, volumes = cylindricalVolumes)

#neutron flux on cartesian mesh
nFluxMean = neutronMeshTally.get_reshaped_data(value='mean').flatten()
nFluxStddev = neutronMeshTally.get_reshaped_data(value='std_dev').flatten()
nFluxPercent = np.nan_to_num(np.divide(nFluxStddev, nFluxMean))
cylindricalVolumes = cylindricalVolumes.T.flatten() #cm3

nFluxMean = nFluxMean*neutronsPerSecond #particle-cm/s
nFluxMean = np.divide(nFluxMean,cylindricalVolumes) #particles/(cm2s)

nFluxStddev = nFluxStddev*neutronsPerSecond #particle-cm/s
nFluxStddev = np.divide(nFluxStddev,cylindricalVolumes) #particles/(cm2s)

cylindricalMesh.write_data_to_vtk(
    filename="cylindricalMesh.vtk",
    datasets={"heating w/cm3": cylindricalMeshHeatingMean,
              "std dev w/cm3": cylindricalMeshHeatingStddev,
              "N flux, N/cm2s": nFluxMean,
              #"N flux stddev, N/cm2s": nFluxStddev
              "N flux stddev percent of mean": nFluxPercent
    },
    volume_normalization = False
)

print("Total Heating in cylindricalg Mesh, MW: ", np.sum(np.multiply(cylindricalMeshHeatingMean, cylindricalVolumes.T.flatten()))/1e6)

#calculate heating in unstructured mesh
mean = breederUmeshHeatingTally.get_reshaped_data(value='mean')
stddev = breederUmeshHeatingTally.get_reshaped_data(value='std_dev')
umeshHeatingMean = mean[:,0,0]
umeshHeatingStddev = stddev[:,0,0]
umesh = meshes[4]
volumes = umesh.volumes
umeshHeatingMean, umeshHeatingStddev = tallierizer.calcHeating(umeshHeatingMean, umeshHeatingStddev, power, volumes)
print("Total Heating in breeder umesh MW", np.sum(np.multiply(umeshHeatingMean, volumes.T.flatten()))/1e6)

#heating in breeder cell
mean = breederHeatingTally.get_reshaped_data(value='mean')
stddev = breederHeatingTally.get_reshaped_data(value='std_dev')
mean = mean[:,0,0]
stddev = stddev[:,0,0]
breederCellMeanHeating, breederCellStddevHeating = tallierizer.calcHeating(mean,stddev,power)
print("Total Heating in breeder Cell MW: ", breederCellMeanHeating/1e6)
print("Std dev MW: ", breederCellStddevHeating/1e6)

#tritium breeding in unstructured mesh
mean = breederUmeshTBRTally.get_reshaped_data(value='mean')
stddev = breederUmeshTBRTally.get_reshaped_data(value='std_dev')
umesh = meshes[4]
umeshTBRmean = mean[:,0,0]
umeshTBRstddev = stddev[:,0,0]
volumes = umesh.volumes.T.flatten()
print("Total TBR in breeder mesh: ", np.sum(umeshTBRmean))
print("Std Dev: ", np.sum(umeshTBRstddev))
umeshTBRmean = np.divide(umeshTBRmean, volumes)
umeshTBRstddev = np.divide(umeshTBRstddev, volumes)

#tritium breeding in breeder layer
mean = breederTBRTally.get_reshaped_data(value='mean')
stddev = breederTBRTally.get_reshaped_data(value='std_dev')
TBRmean = mean[:,0,0]
TBRstddev = stddev[:,0,0]
print("Total TBR in breeder layer: ", TBRmean)
print("Std Dev: ", TBRstddev)

#write out unstructured mesh values
umesh.write_data_to_vtk(
    filename = "breederMesh.vtk",
    datasets = {"heating": umeshHeatingMean,
                "heating std dev": umeshHeatingStddev,
                "TBR": umeshTBRmean,
                "TBR std dev": umeshTBRstddev},
    volume_normalization = False
)

#write source mesh to vtk
sourceMesh = meshes[1]
#load source info
with open('strengths.pickle', 'rb') as file:
	strengths = np.array(pickle.load(file))


sourceMesh.write_data_to_vtk(
    filename = "sourceStrengths.vtk",
    datasets = {
        "strengths": strengths
    },
    volume_normalization = False
)
