import parametric_stellarator
import openmc


# NOTE FOR EDGAR AND JOSH:
"""
This script creates a single period while also creating all magnets so there is a geometry mismatch. If actually using this script, I'd recommend either taking the magnets out while generating one period or generating all four periods with the magnets.

If using a full (four-period) geometry, the geometry definition in OpenMC will need to be adjusted. The easiest way to do that is to just fill the vacuum surface (vac_surf) with the dagmc.h5m (dag_univ).

Let me know if you have any questions!
"""


# Define plasma equilibrium VMEC file
plas_eq = 'plas_eq.nc'
# Define number of periods in stellarator plasma
num_periods = 1
# Define radial build
radial_build = {
    'sol': {'thickness': 10, 'h5m_tag': 'Vacuum'},
    'first_wall': {'thickness': 5},
    #'breeder': {'thickness': 50},
    #'back_wall': {'thickness': 5},
    #'shield': {'thickness': 20}
}
# Define number of periods to generate
gen_periods = 1
# Define number of toroidal cross-sections to make
num_phi = 60
# Define number of poloidal points to include in each toroidal cross-section
num_theta = 100
# Define magnet coil parameters
magnets = {
    'file': 'coils.txt',
    'cross_section': ['circle', 20],
    'start': 3,
    'stop': None,
    'name': 'magnet_coils',
    'h5m_tag': 'magnets'
}
# Define source mesh parameters
source = {
    'num_s': 11,
    'num_theta': 81,
    'num_phi': 241
}
# Define export parameters
export = {
    'exclude': [],
    'graveyard': False,
    'step_export': True,
    'h5m_export': 'Cubit',
    'plas_h5m_tag': 'Vacuum',
    'facet_tol': 1,
    'len_tol': 5,
    'norm_tol': None
}

# Create stellarator
strengths = parametric_stellarator.parametric_stellarator(
    plas_eq, num_periods, radial_build, gen_periods, num_phi, num_theta,
    magnets = None, source = source,
    export = export
    )

# Define materials in OpenMC

# Define tungsten
W = openmc.Material()
W.add_element('W', 1.0)
W.set_density('g/cm3', 19.35)

# Define reduced-activation ferritic martensitic (RAFM) steel
RAFM = openmc.Material()
RAFM.add_element('Fe', 0.895, 'wo')
RAFM.add_element('Cr', 0.09, 'wo')
RAFM.add_element('W', 0.015, 'wo')
RAFM.set_density('g/cm3', 7.8)

# Define lead-lithium eutectic coolant/breeder
PbLi = openmc.Material()
PbLi.add_element('Pb', 83.0, 'ao')
PbLi.add_element(
    'Li', 17.0,  'ao', enrichment = 90.0, enrichment_target = 'Li6'
)
PbLi.set_density('g/cm3', 9.806)

# Define helium coolant
He = openmc.Material()
He.add_element('He', 1.0)
He.set_density('g/cm3', 0.00572)

# Define silicon carbide
SiC = openmc.Material()
SiC.add_element('Si', 1, 'ao')
SiC.add_element('C', 1, 'ao')
SiC.set_density('g/cm3', 3.21)

# Define water
H2O = openmc.Material()
H2O.add_element('H', 2, 'ao')
H2O.add_element('O', 1, 'ao')
H2O.set_density('g/cm3', 1.0)

# Define tungsten carbide
WC = openmc.Material()
WC.add_element('W', 1, 'ao')
WC.add_element('C', 1, 'ao')
WC.set_density('g/cm3', 15.63)

# Define first wall material
first_wall = openmc.Material.mix_materials(
    [W, RAFM, He], [0.04565, 0.323, 0.627], 'vo',
    name = 'first_wall'
    )


# Add materials to OpenMC model
materials = openmc.Materials(
    [first_wall]
)
# Export materials XML
materials.export_to_xml()

# Define geometry in OpenMC

# Define DAGMC universe
dag_univ = openmc.DAGMCUniverse('dagmc.h5m')

# Define problem outer boundary
vac_surf = openmc.Sphere(r = 10000, surface_id = 9999, boundary_type = 'vacuum')
# Define transmission boundary for period model at 0 degrees
trans_x = openmc.XPlane(
    boundary_type = 'transmission',
    surface_id = 9990
)
# Define transmission boundary for period model at 90 degrees
trans_y = openmc.YPlane(
    boundary_type = 'transmission',
    surface_id = 9991
)

# Define first period of geometry
region1  = -vac_surf & +trans_x & +trans_y
period1 = openmc.Cell(cell_id = 9996, region = region1, fill = dag_univ)
# Define second period of geometry
region2  = -vac_surf & -trans_x & +trans_y
period2 = openmc.Cell(cell_id = 9997, region = region2, fill = dag_univ)
period2.rotation = [0, 0, 90]
# Define third period of geometry
region3  = -vac_surf & -trans_x & -trans_y
period3 = openmc.Cell(cell_id = 9998, region = region3, fill = dag_univ)
period3.rotation = [0, 0, 180]
# Define fourth period of geometry
region4  = -vac_surf & +trans_x & -trans_y
period4 = openmc.Cell(cell_id = 9999, region = region4, fill = dag_univ)
period4.rotation = [0, 0, 270]

# Add geometry to OpenMC model
geometry = openmc.Geometry([period1, period2, period3, period4])
# Export geometry XML
geometry.export_to_xml()

# Define run settings
settings = openmc.Settings()
settings.run_mode = 'fixed source'
settings.particles = 1000
settings.batches = 10

# Define source
settings.source = []

# Define source mesh
mesh = openmc.UnstructuredMesh("SourceMesh.h5m", 'moab')

src = openmc.Source()
src.space = openmc.stats.MeshSpatial(
    mesh, strengths = strengths, volume_normalized = False
)
src.angle = openmc.stats.Isotropic()
src.energy = openmc.stats.Discrete([14.1e6], [1.0])
settings.source = [src]

# Export settings XML
settings.export_to_xml()

# Define TBR tally
TBR = openmc.Tally(name = 'TBR')
TBR.scores = ['H3-production']

# Compile tallies
tallies = openmc.Tallies([TBR])
# Export tallies XML
tallies.export_to_xml()

# Run simulation
openmc.run()

# Access statepoint file
sp = openmc.StatePoint('statepoint.10.h5')

# Extract and store TBR result
TBR_tally = sp.get_tally(name = 'TBR')
TBR_dataframe = TBR_tally.get_pandas_dataframe()
TBR_mean = TBR_dataframe['mean'].sum()
TBR_std_dev = TBR_dataframe['std. dev.'].sum()
# Extract and store leakage result
leakage = sp.global_tallies[3]
leakage_mean = leakage[3]
leakage_std_dev = leakage[4]

# Close statepoint file
sp.close()

# Print tallies to screen
print(f'leakage = {leakage_mean} +/- {leakage_std_dev}')
print(f'TBR = {TBR_mean} +/- {TBR_std_dev}')
