import openmc
import numpy as np



def neutronics(strengths, mats, particles = 10000, batches = 5):

    periodic1 = openmc.XPlane(boundary_type = 'periodic', surface_id = 9998)
    periodic2 = openmc.YPlane(boundary_type='periodic', surface_id = 9997)
    
    dagUniv = openmc.DAGMCUniverse('dagmc.h5m')
    dagBoundingBox = dagUniv.bounding_box

    #make a sphere slightly larger than the dagmc bounding box as the vac surf
    vacSurf = openmc.Sphere(r = np.sum(np.multiply((dagBoundingBox[1]-dagBoundingBox[0]),(dagBoundingBox[1]-dagBoundingBox[0])))**0.5+100,
                            boundary_type='vacuum', surface_id = 9996)

    region1 = -vacSurf & +periodic1 & +periodic2 #the region must be in the normal direction of both planes
    period1 = openmc.Cell(region=region1, fill = dagUniv, cell_id=9999, name = "period1")


    geometry = openmc.Geometry([period1])
    geometry.export_to_xml()


    #some settings
    settings = openmc.Settings()
    settings.run_mode = 'fixed source'
    settings.particles = particles
    settings.batches = batches
    settings.photon_transport = True

    #source settings
    mesh = openmc.UnstructuredMesh("SourceMesh.h5m",'moab')
    source = openmc.IndependentSource()
    source.space = openmc.stats.MeshSpatial(
        mesh, strengths = strengths, volume_normalized = False
    )
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14.1e6],[1.0]) #an actual spectrum might be good
    settings.source = [source]

    settings.export_to_xml()

    #create meshes for visualizing neutronics
    cylindricalMesh = openmc.CylindricalMesh(
        r_grid = np.linspace(76327, 77077,66),
        z_grid = np.linspace(-425,425,86),
        phi_grid = np.linspace(0.771,0.799,100),
        origin = np.array([-53604,-53604,0])
    )

    #nuclear heating mesh tally
    cylindricalMeshFilter = openmc.MeshFilter(cylindricalMesh)
    heatingMeshTally = openmc.Tally(name = "Cartesian Mesh Heating Tally")
    heatingMeshTally.filters = [cylindricalMeshFilter]
    heatingMeshTally.scores = ['heating'] #eV/source, flux
    
    #neutron flux mesh tally
    neutronMeshTally = openmc.Tally(name = "Cartesian Mesh Neutron Flux Tally")
    nfilter = openmc.ParticleFilter(['neutron'])
    neutronMeshTally.filters=[cylindricalMeshFilter, nfilter]
    neutronMeshTally.scores = ['flux'] #particle cm/source

    #FW DPA Cell tally
    fwFilter = openmc.CellFilter([2])
    fwDPATally = openmc.Tally(name = "FW DPA Tally")
    fwDPATally.filters = [fwFilter]
    fwDPATally.nuclides = ["Fe54", "Fe56", "Fe57", "Fe58"]
    fwDPATally.scores = ['damage-energy'] #eV/source particle
    

    #FW Heating Cell Tally
    fwHeatingTally = openmc.Tally(name="FW Heating Tally")
    fwHeatingTally.filters = [fwFilter]
    fwHeatingTally.scores = ['heating'] #ev/source

    #FW DPA mesh tally
    fwMesh = openmc.UnstructuredMesh('vacVessel.h5m', library='moab')
    fwMeshFilter = openmc.MeshFilter(fwMesh)
    fwDPAmeshTally = openmc.Tally(name = 'FW DPA Mesh Tally')
    fwDPAmeshTally.filters = [fwMeshFilter]
    fwDPAmeshTally.nuclides = ["Fe54", "Fe56", "Fe57", "Fe58"]
    fwDPAmeshTally.scores = ['damage-energy']

    #FW Mesh heating tally
    fwHeatingMeshTally = openmc.Tally(name='FW Heating Mesh Tally')
    fwHeatingMeshTally.filters = [fwMeshFilter]
    fwHeatingMeshTally.scores = ['heating']


    #TBR in breeder tally
    breederFilter = openmc.CellFilter([3])
    breederTBRTally = openmc.Tally(name = "Breeder TBR Tally")
    breederTBRTally.filters = [breederFilter]
    breederTBRTally.nuclides = ['Li6','Li7']
    breederTBRTally.scores = ["H3-production"] #tbr

    #Heating in breeder tally
    breederHeatingTally = openmc.Tally(name = "Breeder Heating Tally")
    breederHeatingTally.filters = [breederFilter]
    breederHeatingTally.scores = ["heating"] #ev/source

    #TBR in breeder mesh tally
    breederUmesh = openmc.UnstructuredMesh('breeder.h5m', library='moab')
    breederMeshFilter = openmc.MeshFilter(breederUmesh)
    breederUmeshTBRTally = openmc.Tally(name="Breeder Mesh TBR Tally")
    breederUmeshTBRTally.filters = [breederMeshFilter]
    breederUmeshTBRTally.nuclides = ['Li6','Li7']
    breederUmeshTBRTally.scores = ["H3-production"] #tbr

    #Heating in breeder mesh tally
    breederUmeshHeatingTally = openmc.Tally(name="Breeder Mesh Heating Tally")
    breederUmeshHeatingTally.filters = [breederMeshFilter]
    breederUmeshHeatingTally.scores = ["heating"] #ev/source
    
    tallies = openmc.Tallies([heatingMeshTally,
                              neutronMeshTally,
                              fwDPATally,
                              fwDPAmeshTally,
                              breederTBRTally,
                              breederHeatingTally,
                              breederUmeshHeatingTally,
                              breederUmeshTBRTally,
                              fwHeatingMeshTally,
                              fwHeatingTally
                              ])
    

    model = openmc.Model(materials = mats, geometry=geometry, tallies=tallies, settings = settings)

    return model
    
def wallLoading(strengths, mats, particles = 10000, batches = 5):
    periodicX = openmc.XPlane(boundary_type='periodic', surface_id = 9998) #assign these to avoid conflicts with dagmc
    periodicY = openmc.YPlane(boundary_type='periodic', surface_id = 9997)
    
    dagUniv = openmc.DAGMCUniverse('fwdagmc.h5m')
    boundingBox = dagUniv.bounding_box
    r = np.sqrt(np.sum(boundingBox[0]**2))*2

    
    vacSurf = openmc.Sphere(r=r,boundary_type='vacuum', surface_id = 9996)

    region1 = -vacSurf & +periodicX & +periodicY
    period1 = openmc.Cell(region=region1, fill = dagUniv, cell_id=9999)

    geometry = openmc.Geometry([period1])
    geometry.export_to_xml()

    #some settings
    settings = openmc.Settings()
    settings.run_mode = 'fixed source'
    settings.particles = particles
    settings.batches = batches
    settings.photon_transport = True

    #source settings
    mesh = openmc.UnstructuredMesh("SourceMesh.h5m",'moab')
    source = openmc.IndependentSource()
    source.space = openmc.stats.MeshSpatial(
        mesh, strengths = strengths, volume_normalized = False
    )
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14.1e6],[1.0])
    settings.source = [source]
    settings.export_to_xml()

    #nwl tally
    fwMesh = openmc.UnstructuredMesh("fwUmesh.h5m", library='moab')
    fwMeshFilter = openmc.MeshFilter(fwMesh)
    fromSOLfilter = openmc.CellFromFilter([2])
    fwNWLtally = openmc.Tally(name = "NWL Tally")
    fwNWLtally.filters = [fwMeshFilter,fromSOLfilter]
    fwNWLtally.scores = ['current'] #particles/source
    
    tallies = openmc.Tallies([fwNWLtally])

    model = openmc.Model(materials = mats, geometry = geometry, tallies = tallies, settings = settings)

    return model
