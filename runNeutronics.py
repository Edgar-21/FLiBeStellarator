import openmc
import neutronics
import pickle

#load source info
with open('strengths.pickle', 'rb') as file:
	strengths = pickle.load(file)

mats = openmc.Materials.from_xml('materials.xml')
model = neutronics.neutronics(strengths, mats)



p = openmc.Plot()
p.width = (150, 150.0)
p.pixels = (400, 400)
p.color_by = 'material'

plots = openmc.Plots([p])
plots.export_to_xml()


model.run()
