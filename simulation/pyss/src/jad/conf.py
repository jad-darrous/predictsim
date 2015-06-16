
weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1)]
#weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1), (0, 0, 0, 0, 0, -1)]
# weights_options = [(1, 0, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1, 0), (0, 0, 0, 0, 0, -1, 0)]

weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1)]
weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0)]


indices = (2,3,4,5,11)
indices = (2,3,4,5,9)


#indices = (2,3,4,5,11, 8,9,15)


mp = {
	"CEA-curie_sample_log":  4,
	"CEA-curie_cut_log":  8*8,

	"KTH-SP2_log": 256,
	"CTC-SP2_log": 256,
	"SDSC-SP2_log": 512,
	"SDSC-BLUE_log": 1024,
	"CEA-curie_log": 1024,
	"Metacentrum2013": 1024,
}
training_parts = mp[fname.split('.')[0]]
del mp

training_percentage = 0.7
