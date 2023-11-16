import openmc
import numpy as np

with openmc.StatePoint('statepoint.5.h5') as sp:
    heatingMeshTally = sp.get_tally(name = "Heating Mesh Tally")
    fwDPATally = sp.get_tally(name="FW DPA Tally")
    breederTBRTally = sp.get_tally(name = "Breeder TBR Tally")

mats = openmc.Materials.from_xml('materials.xml')
fwMat = mats[11] #FNSFFWstruct
fwVol = 15909811.971955 #from cubit

def calcDPAIron(dpaTally, power, material, volume):
    
    #calculate DPA per FPY based on the following constants
    
    Ed = 40 #eV, displacement energy in iron
    displacementEfficiency = 0.8
    energyPerFusion = 17.6e6 #eV
    eVtoJ = 1.60218e-19 #J/eV
    sourceNeutronsPerYear = power/(energyPerFusion*eVtoJ)*60*60*24*365.25

    #get tally info
    
    #atom density
    FeDensity = 0
    for i in dpaTally.nuclides:
        FeDensity += material.get_nuclide_atom_densities()[i]
    FeDensity = FeDensity/(1e-24) #to atoms/cm3

    #damage energy stats
    damageEnergy = dpaTally.mean.sum()
    stDev = dpaTally.std_dev.sum()

    #mean DPA
    displacementsPerSource = damageEnergy*displacementEfficiency/(2*Ed)
    displacementsPerFPY = displacementsPerSource*sourceNeutronsPerYear
    numFe = FeDensity*volume
    DPAmean = displacementsPerFPY/numFe

    #std dev DPA
    DPAstDev = DPAmean/damageEnergy*stDev

    return DPAmean, DPAstDev

#calculate fw DPA
DPAfw, DPAstdevFw, = calcDPAIron(fwDPATally,500e6,fwMat, fwVol)

print(DPAfw)
print(DPAstdevFw)

#calculate heating in mesh
cylindricalMesh = openmc.CylindricalMesh(r_grid = np.array([1170,1200]),
                                             z_grid = np.linspace(-500,500, 50),
                                             phi_grid = np.linspace(0, np.pi/2,30)
                                             )


mean = heatingMeshTally.get_reshaped_data(value='mean')
meanHeating = mean[:,0,0]
meanLocal = mean[:,0,1]

cylindricalMesh.write_data_to_vtk(
    filename="meshHeating.vtk",
    datasets={"heating: ":meanHeating,
              "heatingLocal: ":meanLocal}
)




