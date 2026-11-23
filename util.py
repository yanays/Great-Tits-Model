from configuration import *
import matplotlib.pyplot as plt
import matplotlib.axis as ax
from matplotlib import ticker
from globals import *


def zeros_after_point(v):
    l = 0

    if v>1:
        return 0

    for _ in range(10):
        if 10 ** (-l) < v:
            return l-1
        l += 1
    return "ERROR"


def round_for_model(v, more=0):
    if v==0:
        return 0
    n_0 = zeros_after_point(v)
    ndigits = 1 if v>1 else n_0+2
    ndigits+=more
    return round(v, ndigits)


def seasons_to_years(lists):
    return [sum(l) for l in lists]


def average_lists(lists):
    return [average_ignore_invalid([l[i] for l in lists]) for i in range(len(lists[0]))]


def average_ignore_invalid(l):
    new_l = [x for x in l if x!="invalid"]
    return average(new_l)


def average(l):
    return sum(l)/len(l)


def average_for_model(l, years_to_ignore):
    return sum(l[years_to_ignore:])/(len(l)-years_to_ignore)


def proportion(l1, l2):
    # The rate of l1 out of l2
    new_l2 = [v if v>0 else 1 for v in l2]
    return [l1[i]/new_l2[i] for i in range(len(l1))]


def sum_lists(l1, l2):
    return [l1[i]+l2[i] for i in range(len(l1))]


def histogram_brood_size(L):
    Y = [0]*13
    for y in L:
        Y[y]+=1
    return Y


def there_is_male(nests, i):
    for pair in nests.keys():
        if pair[0]==i:
            return True
    return False


def reset_globals():
    for G in [TOTAL_AGE, TOTAL_AGE_BY_SPRINGS, TOTAL_DEATHS, BOXES_IN_USE, PROB_TO_BE_EATEN, BROOD_SIZE]:
        G[0] = 0

    CONDITIONS.clear()
    AGES.clear()
    AGES_BY_SPRINGS.clear()
    for _ in range(INIT_N_BIRDS):
        CONDITIONS.append(0)
        AGES.append(1)
        AGES_BY_SPRINGS.append(1)

    for L in [NESTS, CHICKS_IN_NESTS, LIMITED_NESTS, ALL_LAZIES, ALL_DILIGENTS, EXTINCTION, BROOD_SIZES, PROB_TO_BE_EATEN_ALL_YEARS, ENERGY_AFTER_FUNCTIONING]:
        L.clear()

    for L in [TOTAL_DEATHS_ADULT_YOUNG, PREDATION_ADULT_YOUNG, DISEASE_DEATH_ADULT_YOUNG, POPULATION_SIZE_ADULT_YOUNG, NUMBER_OF_PAIRS, SURVIVAL_RATES_WINTER_ADULT_YOUNG]:
        L[0] = 0
        L[1] = 0

    for G in [TO_COUNT_DATA, UNUSUAL_YEAR]:
        G[0]=False

    INVALID_YEARS["survival_rate_young"] = 0
    INVALID_YEARS["brood_size"] = 0
    INVALID_YEARS["condition_young"] = []


DATA_TYPES = ["Hatchlings per Adult per Year", "Hatchlings per Year", "Life Expectancy by Springs", "Life Expectancy by Winters", "Average Condition at the Beginning of Winter", "Starvation", "Population Size Before Spring", "Population Size Before Winter", "Young Ratio"]

PERIODS_LIST = [i*2 for i in range(N_BREEDING_PERIODS+1)]
DATA_WITH_SEASONS = ["Death from Disease by Periods", "Hatchlings by Periods"] # , "Population Size During Spring"]

SMALL_SIZE = 13
MEDIUM_SIZE = 13
BIGGER_SIZE = 19

# ax.YAxis.set_major_formatter(ticker.StrMethodFormatter("{x:.2f}"))

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title