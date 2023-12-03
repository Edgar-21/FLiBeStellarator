import openmc

with openmc.StatePoint('statepoint.6.h5') as sp:
    fwNWLtally = sp.get_tally(id=1)
    meshes = sp._meshes

fwMesh = meshes[2]
meanNWL = fwNWLtally.get_reshaped_data("mean").flatten()

fwMesh.write_data_to_vtk(
    filename = "FWNWL.vtk",
    datasets = {
        "NWL":meanNWL
    },
    volume_normalization = False
)