
#
# geenral parameters
#

weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1)]
#weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1), (0, 0, 0, 0, 0, -1)]


weights_options = [(1, 0, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1, 0), (0, 0, 0, 0, 0, -1, 0)]
weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0),
(0, 0, 0, 0, 0, +1), (0, 0, 0, 0, 0, -1), (0, -1, 0, 0, 0, 0)]

weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1)]

weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0)]

if random_weights:
	import random
	# weights_options = set()
	# weights_options.add((1, 0, 0, 0, 0, 0))
	# weights_options.add((0, 1, 0, 0, 0, 0))
	# weights_options.add((0, 0, 0, 0, 0, 1))
	# weights_options.add((-1, 0, 0, 0, 0, 0))
	# weights_options.add((0, -1, 0, 0, 0, 0))
	# weights_options.add((0, 0, 0, 0, 0, -1))
	# for _ in range(10000):
	# 	w = [0] * 3
	# 	for i in range(3):
	# 		w[i] = random.randint(0, 3) * ([+1, -1][random.randint(0, 1)])
	# 	m = min(w)
	# 	# w = map(lambda u: u-m, w)
	# 	w[2:2] = [0]*3 # for the user, bypass and admin
	# 	weights_options.add(tuple(w))

	weights_options = []
	for x1 in range(-3, 4):
		for x2 in range(-3, 4):
			for x3 in range(-3, 4):
				weights_options.append((x1, x2, 0,0,0, x3))

	weights_options = []
	weights_options.append((1, 0, 0, 0, 0, 0))
	weights_options.append((0, 1, 0, 0, 0, 0))
	weights_options.append((0, 0, 0, 0, 0, 1))
	weights_options.append((-1, 0, 0, 0, 0, 0))
	weights_options.append((0, -1, 0, 0, 0, 0))
	weights_options.append((0, 0, 0, 0, 0, -1))

	# weights_options = sorted(weights_options)
	print "#weights_options", len(weights_options), weights_options


indices = (2,3,4,5,11)
indices = (2,3,4,5,9)


# indices = (2,3,4,5,11, 8,9,15)

#
# Offline learning parameters
#

mp = {
	"CEA-curie_sample_log":  4,
	"CEA-curie_cut_log":  8*8,

	"KTH-SP2_log": 256/2,
	"CTC-SP2_log": 256,
	"SDSC-SP2_log": 512,
	"SDSC-BLUE_log": 1024,
	"CEA-curie_log": 1024,
	"Metacentrum2013": 1024,
}
training_parts = mp[fname.split('.')[0]]
del mp


training_percentage = 0.01

training_percentage = 0.7

# training_parts = int(training_parts * training_percentage / 0.7)
# training_parts = 1
