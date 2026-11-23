from configuration import *

TOTAL_AGE = [0]
TOTAL_AGE_BY_SPRINGS = [0]
TOTAL_DEATHS = [0]
BOXES_IN_USE = [0]
PROB_TO_BE_EATEN = [0]     # The probability for a certain food to be eaten by any bird; = 1 - (1-prob_to_eat) ^ n_birds

# lists of birds:
CONDITIONS = [0]*INIT_N_BIRDS
AGES = [1]*INIT_N_BIRDS
AGES_BY_SPRINGS = [1]*INIT_N_BIRDS
NESTS = {}   # (bird1, bird2): [number of offsprings, active_flag]
             # active_flag: True --> alive; False --> dead, "spot" --> not active

CHICKS_IN_NESTS = []  # Each row represents one year, and each value represents the number of chicks for one pair
LIMITED_NESTS = []  # Pairs whose brood size is particularly limited. Listed by bird1.

ALL_LAZIES = []
ALL_DILIGENTS = []
EXTINCTION = []

BROOD_SIZES = []

# For an empirical determination of parameters
YEAR_TO_START_COUNT = FIRST_YEARS_TO_IGNORE
TO_COUNT_DATA = [False]
TOTAL_DEATHS_ADULT_YOUNG = [0, 0]  # adults, young
PREDATION_ADULT_YOUNG = [0, 0]
DISEASE_DEATH_ADULT_YOUNG = [0, 0]
POPULATION_SIZE_ADULT_YOUNG = [0, 0]
NUMBER_OF_PAIRS = [0,0]
SURVIVAL_RATES_WINTER_ADULT_YOUNG = [0, 0]
BROOD_SIZE = [0]
PROB_TO_BE_EATEN_ALL_YEARS = []

UNUSUAL_YEAR = [False]
ENERGY_AFTER_FUNCTIONING = []

# For multi-simulations
UNUSUAL_BROOD_SIZE = []


INVALID_YEARS = {"survival_rate_adult": 0, "survival_rate_young": 0, "brood_size": 0, "condition_young": [], "condition_adults": []}