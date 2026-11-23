# In each list, the first value is the baseline,
# so it will not be tested in the serial simulation.

X_encounter_rate = [x/20 for x in range(20,50)]
X_brood_size = list(range(12,3,-1))
X_partial_brood_size = list(range(12,3,-1))
X_resource_threshold = [x/10 for x in range(10, -1, -1)]