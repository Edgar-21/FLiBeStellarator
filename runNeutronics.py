import openmc
import neutronics
import pickle

#load source info
with open('strengths.pickle', 'rb') as file:
	strengths = pickle.load(file)

mats = openmc.Materials.from_xml('materials.xml')
#model = neutronics.wallLoading(strengths, mats, particles=1000000, batches=6)
model = neutronics.neutronics(strengths, mats, particles=1000000, batches=5)
model.export_to_model_xml()
model.run()

p = openmc.Plot()
p.width = (150, 150.0)
p.pixels = (400, 400)
p.color_by = 'material'

plots = openmc.Plots([p])
plots.export_to_xml()



