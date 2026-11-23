from simulation import *
from calibration import *
from print_graphs import *

# ###########################
# # Running the simulation  #
# ###########################

# simulate_and_print(100)
# # Single simulation.
# # Parameters:
# #   n_years: number of years [int].
# #   unusual_food [optional]: change, by a factor, the food amount in (or from) a specific year [None or (year, factor)].
# #   unusual_death [optional]: adding annual top-down mortality amount in (or from) a specific year [None or (year, season_idx, death_ratio, p)].
# #                                                                                                                    year: [int or "all"].
# #                                                                                                                    season_idx: specific breeding period [int or "all"].
# #                                                                                                                    p: probability of activating the unusual_death in a relevant year.
# #   hard_winter [optional]: change, by a factor, the mean winter survival threshold in (or from) a specific year [None or (year, factor)].
# #   unusual_nesting_boxes [optional]: change, by a factor, the maximal number of pairs in (or from) a specific year [None or (year, factor)].
# #   permanent_flag [optional]: set the changes to be from the specified year, rather than in this year only [boolean].

serial_simulation(40, None, 20)
# # Serial simulation with a change in one of the parameters from one simulation to another.
# # The ranges of the values are taken from independent_variable_ranges.py.
# # Parameters:
# #   n_years: number of years [int].
# #   parameter: the changing independent parameter:
# #     "maximum brood size"
# #     "partial brood limit"
# #     "encounter probability"
# #     "resource for winter"


# #########################
# # Analysing the results #
# #########################

# print_results("brood size")
# # Print the graphs of the data from results folder. files:
# #   results_brood_size.py,
# #   results_partial_brood_limit.py,
# #   results_encounter_rate.py,
# #   results_resource_threshold.py
# #
# # Parameters:
# #   experiment: indicates for the changing independent parameter:
# #     "brood size"
# #     "partial brood size"
# #     "encounter probability"
# #     "resource threshold"


# ##############################
# # Calibration and validation #
# ##############################

# validate_food_reproduction()
# # Testing the effect of increasing the food amount in one year on the reproduction.

# find_edge_values()
# # Finds the ANNUAl_FOOD values corresponding to RESOURCE_FOR_SURVIVAL_WINTER and PROB_TO_STOP_NESTING edge values.
# # Designed for finding a linear function of food quantity for grid-search.
# # Parameters:
# #   threshold_values [optional]: edge values for RESOURCE_FOR_SURVIVAL_WINTER [(int1, int2)].
# #   p_stop_values [optional]: edge values for PROB_TO_STOP_NESTING [(float1, float2, float3)].
# #
# # Print:
# #   ANNUAl_FOOD list for (int1 and float1, int1 and float2, int2 and float1, int2 and float2)
# #   ANNUAl_FOOD list for (int1 and float2, int1 and float3, int2 and float2, int2 and float3)

# validate_linear_function()
# # Validating the linear function of food by RESOURCE_FOR_SURVIVAL_WINTER and PROB_TO_STOP_NESTING