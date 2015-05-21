
weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1)]
#weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1), (0, 0, 0, 0, 0, -1)]
# weights_options = [(1, 0, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1, 0), (0, 0, 0, 0, 0, -1, 0)]

weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1)]


indices = (2,3,4,5,11)
indices = (2,3,4,5,9)


#indices = (2,3,4,5,11, 8,9,15)


mp = {
	"CEA-curie_sample_log": (0.6, 4),
	"KTH-SP2_log": (0.6, 6),
	"CTC-SP2_log": (0.6, 8),
	"SDSC-SP2_log": (0.6, 16),
	"CEA-curie_cut_log": (0.8, 16),
	"CEA-curie_log": (0.8, 16),
	"SDSC-BLUE_log": (0.8, 32),
}
training_percentage, training_parts = mp[fname.split('.')[0]]
del mp
