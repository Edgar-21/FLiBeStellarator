import openmc
import numpy as np



def neutronics(strengths, mats, particles = 10000, batches = 5):


    periodicX = openmc.XPlane(boundary_type='periodic', surface_id = 9998) #assign these to avoid conflicts with dagmc
    periodicY = openmc.YPlane(boundary_type='periodic', surface_id = 9997)
    
    dagUniv = openmc.DAGMCUniverse('dagmc.h5m')
    print(dagUniv.material_names)
    dagBoundingBox = dagUniv.bounding_box

    
    
    print(np.sum(np.multiply(dagBoundingBox[0],dagBoundingBox[0]))*0.5+100)
    vacSurf = openmc.Sphere(r=np.sum(np.multiply(dagBoundingBox[0],dagBoundingBox[0]))*0.5+100,
                            boundary_type='vacuum', surface_id = 9996)

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

    #create meshes for visualizing neutronics
    cylindricalMesh = openmc.CylindricalMesh(r_grid = np.array([1170,1200]),
                                             z_grid = np.linspace(-500,500, 50),
                                             phi_grid = np.linspace(0, np.pi/2,30)
                                             )

    #nuclear heating mesh tally
    cylindricalMeshFilter = openmc.MeshFilter(cylindricalMesh)
    heatingMeshTally = openmc.Tally(name = "Heating Mesh Tally")
    heatingMeshTally.filters = [cylindricalMeshFilter]
    heatingMeshTally.scores = ['heating', 'heating-local'] #eV/source
    
    #FW DPA tally
    fwFilter = openmc.CellFilter([2])
    fwDPATally = openmc.Tally(name = "FW DPA Tally")
    fwDPATally.filters = [fwFilter]
    fwDPATally.scores = ['damage-energy'] #eV/source particle
    fwDPATally.nuclides = ["Fe54", "Fe56", "Fe57", "Fe58"]

    #TBR in breeder tally
    breederFilter = openmc.CellFilter([3])
    breederTBRTally = openmc.Tally(name = "Breeder TBR Tally")
    breederTBRTally.filters = [breederFilter]
    breederTBRTally.scores = ["H3-production"]
    breederTBRTally.nuclides = ['Li6', 'Li7']

    tallies = openmc.Tallies([heatingMeshTally, fwDPATally, breederTBRTally])

    model = openmc.Model(materials = mats, geometry=geometry, tallies=tallies, settings = settings)

    return model
    

