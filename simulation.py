import random
import matplotlib.pyplot as plt
import numpy as np
from util import *
import os
from configuration import *
from globals import *
import copy
from independent_variable_ranges import X_brood_size, X_partial_brood_size, X_encounter_rate, X_resource_threshold


def provide_one_food_item():
    will_be_eaten = random.random() < PROB_TO_BE_EATEN[0]
    if will_be_eaten:
        bird_idx = random.choice(range(len(CONDITIONS)))
        CONDITIONS[bird_idx] += 1


def count(l,v):
    s = 0
    for i in l:
        if i==v:
            s+=1
    return s


def provide_periodic_food(periodic_food, food_goal, periodic_resources_lost):
    n_birds = len(CONDITIONS)

    # Provide gross food
    PROB_TO_BE_EATEN[0] = 1 - ((1 - ENCOUNTER_PROBABILITY[0]) ** n_birds)
    for _ in range(periodic_food):
        provide_one_food_item()

    if UNUSUAL_YEAR[0]:  # for tuning parameters
        ENERGY_AFTER_FUNCTIONING.append([])

    # Reduce resources for functioning
    for bird_idx in range(n_birds):
        # Use resources as possible. Bounded from below by 0 if not CREDIT_CARD_RESOURCES.
        simple_minus = CONDITIONS[bird_idx] - periodic_resources_lost
        new_condition = simple_minus if CREDIT_CARD_RESOURCES else max(simple_minus, 0)
        CONDITIONS[bird_idx] = new_condition

        if UNUSUAL_YEAR[0]:  # for tuning parameters
            ENERGY_AFTER_FUNCTIONING[-1].append(simple_minus)


def find_pair(individual_index):
    for pair in NESTS.keys():
        if individual_index in pair:
            return pair
    return -1


LAST_SINGLE = [-1]
def find_next_available_bird(current_food_threshold):
    i = LAST_SINGLE[0]
    while True:
        i+=1
        if i>=len(AGES) or AGES[i]==0:
            return -1
        if CONDITIONS[i]>=current_food_threshold and find_pair(i)==-1:
            LAST_SINGLE[0]=i
            return i


def one_period_of_breeding_season(periodic_food, annual_nesting_boxes, season_idx, periodic_resources_lost):
    LAST_SINGLE[0] = -1
    pre_season_population = len(CONDITIONS)

    # Provide food
    food_goal = RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0] * (season_idx + 1) / N_BREEDING_PERIODS
    provide_periodic_food(periodic_food, food_goal, periodic_resources_lost)

    # Determine resources-saving parameters
    if SAVING_STRATEGY=="linear":
        food_to_save = RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0] * season_idx / N_BREEDING_PERIODS
    elif SAVING_STRATEGY=="full":
        food_to_save = RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0]
    elif SAVING_STRATEGY=="no":
        food_to_save = 0
    elif SAVING_STRATEGY=="half":
        food_to_save = RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0] / 2
    else:
        raise Exception("Invalid SAVING_STRATEGY")

    food_threshold_for_pairs = RESOURCES_FOR_ONE_OFFSPRING + food_to_save
    food_threshold_for_singles = food_threshold_for_pairs + NESTING_ENERGY

    # Set pairs
    while True:
        male = find_next_available_bird(food_threshold_for_singles)
        if male == -1:
            break
        female = find_next_available_bird(food_threshold_for_singles)
        if female == -1:
            break
        if BOXES_IN_USE[0] >= annual_nesting_boxes:
            break

        if random.random() > PROB_TO_START_NESTING:
            continue

        NESTS[(male, female)] = [0, True]
        BOXES_IN_USE[0] += 1

        CONDITIONS[male] -= NESTING_ENERGY
        CONDITIONS[female] -= NESTING_ENERGY

        r = random.random()
        if r < PARTIAL_BROOD_SIZE_LIMIT[1]:
            LIMITED_NESTS.append(male)

    # Reproduction
    for pair in NESTS.keys():
        if NESTS[pair][1] in [False, "stop"]:
            continue

        male, female = pair

        female_eggs_capacity = int((CONDITIONS[female] - food_threshold_for_pairs) / RESOURCES_FOR_ONE_OFFSPRING)
        male_eggs_capacity = int((CONDITIONS[male] - food_threshold_for_pairs) / RESOURCES_FOR_ONE_OFFSPRING)
        maximum_brood_size = PARTIAL_BROOD_SIZE_LIMIT[0] if male in LIMITED_NESTS else MAXIMUM_BROOD_SIZE[0]
        n_eggs = min(female_eggs_capacity, male_eggs_capacity, maximum_brood_size - NESTS[pair][0])

        for day in range(DAYS_IN_PERIOD):
            if n_eggs>0:
                CONDITIONS[female] -= RESOURCES_FOR_ONE_OFFSPRING
                CONDITIONS[male] -= RESOURCES_FOR_ONE_OFFSPRING
                NESTS[pair][0] += 1
                CONDITIONS.append(0)
                AGES.append(0)
                AGES_BY_SPRINGS.append(0)
                n_eggs -= 1
            if random.random() < PROB_TO_STOP_NESTING[0]:
                NESTS[pair][1] = "stop"  # Mark as not active anymore
                break


    post_season_population = len(CONDITIONS)
    return post_season_population-pre_season_population


def advance_one_pair_by_1(pair, after_index):
    a, b = pair
    return (a - int(a>after_index), b - int(b>after_index))


def advance_indexes_of_pairs_by_1(after_index):
    pairs = list(NESTS.keys())
    for pair in pairs:
        nest = NESTS.pop(pair)
        NESTS[advance_one_pair_by_1(pair, after_index)] = nest
    new_limited_nests = []
    for x in LIMITED_NESTS:
        if x>after_index:
            new_limited_nests.append(x-1)
        elif x==after_index:
            new_limited_nests.append(-x)
        else:
            new_limited_nests.append(x)
    for i in range(len(LIMITED_NESTS)):
        LIMITED_NESTS[i] = new_limited_nests[i]


def mark_parent_as_dead(bird_index):
    pair = find_pair(bird_index)
    if type(pair) == tuple:
        nest = NESTS.pop(pair)
        a, b = pair
        if a==bird_index: a=-a
        if b==bird_index: b=-b
        NESTS[(a, b)] = [nest[0], False]  # Mark this pair as "parents are dead"


def one_die(i):
    TOTAL_AGE[0] += AGES[i]
    TOTAL_AGE_BY_SPRINGS[0] += AGES_BY_SPRINGS[i]
    TOTAL_DEATHS[0] += 1
    del CONDITIONS[i]
    del AGES[i]
    del AGES_BY_SPRINGS[i]


def death(ratio, age_group = "all", count_as_disease = False):
    # age_group: "all", "adult", "young"
    count = 0
    for i in range(len(CONDITIONS)-1, -1, -1):
        if age_group=="adult" and AGES[i]==0:
            continue
        if age_group=="young" and AGES[i]>0:
            continue
        to_die = random.random() < ratio
        if to_die:
            if TO_COUNT_DATA[0]==True and count_as_disease:  # for tuning parameters
                age_idx = 0 if AGES[i]>0 else 1
                TOTAL_DEATHS_ADULT_YOUNG[age_idx]+=1
                DISEASE_DEATH_ADULT_YOUNG[age_idx]+=1

            one_die(i)
            mark_parent_as_dead(i)
            advance_indexes_of_pairs_by_1(i)  # Fix all the indexes of the birds in the other pairs
            count+=1
    return count


def spring(current_annual_food = ANNUAl_FOOD[0], unusual_death = None, annual_nesting_boxes = NESTIMG_BOXES):
    # unusual_death = None or (season_idx, death_ratio)
    death_from_disease_all_spring = []
    predation_all_spring = []
    new_births_all_spring = []
    population_size_during_spring = []
    # population_sizes = []
    unusual_dead = 0
    BOXES_IN_USE[0] = 0
    NESTS.clear()
    LIMITED_NESTS.clear()

    periodic_food = int(current_annual_food / N_BREEDING_PERIODS)
    # periodic_adults_predation_ratio = 1 - (1-ADULTS_PREDATION_RATIO) ** (1 / N_BREEDING_PERIODS)
    periodic_resources_lost = RESOURCE_FOR_FUNCTION_SPRING / N_BREEDING_PERIODS


    for i in range(N_BREEDING_PERIODS):
        population_size_during_spring.append(len(CONDITIONS))
        if unusual_death:
            if unusual_death[0] in [i, "all"]:
                n_before = len(CONDITIONS)
                death(unusual_death[1])
                current_unusual_dead = n_before-len(CONDITIONS)
                unusual_dead+=current_unusual_dead

        for j in range(len(AGES_BY_SPRINGS)):
            AGES_BY_SPRINGS[j] += 1/N_BREEDING_PERIODS

        # Food and breeding
        new_births = one_period_of_breeding_season(periodic_food, annual_nesting_boxes, i, periodic_resources_lost)

        # Disease
        periodic_disease_death_rate_young = DISEASE_DEATH_RATIO_COEFFICIENT_YOUNG * len(CONDITIONS)
        periodic_disease_death_rate_adult = DISEASE_DEATH_RATIO_COEFFICIENT_ADULT * len(CONDITIONS)
        death_from_disease_y = death(periodic_disease_death_rate_young, "young", True)
        death_from_disease_a = death(periodic_disease_death_rate_adult, "adult", True)

        death_from_disease_all_spring.append(death_from_disease_y+death_from_disease_a)
        new_births_all_spring.append(new_births)

    if unusual_death and unusual_death[0] in [N_BREEDING_PERIODS, "all"]:
            n_before = len(CONDITIONS)
            death(unusual_death[1])
            current_unusual_dead = n_before - len(CONDITIONS)
            unusual_dead += current_unusual_dead

    # For tuning parameters
    if TO_COUNT_DATA[0]:

        for nest in NESTS.values():
            BROOD_SIZES.append(nest[0])

        alive_nests_brood_sizes = [nest[0] for nest in NESTS.values() if nest[1]]

        n_young = count(AGES, 0)
        n_adults = len(AGES) - n_young
        POPULATION_SIZE_ADULT_YOUNG[0] += n_adults
        POPULATION_SIZE_ADULT_YOUNG[1] += n_young

        if len(alive_nests_brood_sizes) > 0:
            brood_size = sum(alive_nests_brood_sizes) / len(alive_nests_brood_sizes)
            BROOD_SIZE[0] += brood_size
            if UNUSUAL_YEAR[0]:
                UNUSUAL_BROOD_SIZE.append(brood_size)
        else:
            INVALID_YEARS["brood_size"] += 1

    population_size_during_spring.append(len(CONDITIONS))

    predation_adult = death(ADULTS_PREDATION_RATIO, "adult")
    predation_young = death(YOUNG_PREDATION_RATIO, "young")

    predation_all_spring.append(predation_adult)
    predation_all_spring.append(predation_young)

    # For tuning parameters
    if TO_COUNT_DATA[0]:
        TOTAL_DEATHS_ADULT_YOUNG[0] += predation_adult
        PREDATION_ADULT_YOUNG[0] += predation_adult
        TOTAL_DEATHS_ADULT_YOUNG[1] += predation_young
        PREDATION_ADULT_YOUNG[1] += predation_young

        number_of_nests_alive = len([nest for nest in NESTS.values() if (nest[1]==True or nest[1]=="stop")])
        number_of_nests_dead = len([nest for nest in NESTS.values() if (nest[1] == False)])
        NUMBER_OF_PAIRS[0] += number_of_nests_alive
        NUMBER_OF_PAIRS[1] += number_of_nests_dead

    nests_row = [nest[0] for nest in NESTS.values()]
    CHICKS_IN_NESTS.append(nests_row)

    return death_from_disease_all_spring, predation_all_spring, new_births_all_spring, unusual_dead, population_size_during_spring


def winter(factor=1):
    n_young = count(AGES, 0)
    n_adults = len(AGES) - n_young

    average_age_at_beginning_of_winter = sum(AGES) / len(AGES)
    average_condition_at_beginning_of_winter = sum(CONDITIONS) / len(CONDITIONS)

    condition_adult = [CONDITIONS[i] for i in range(len(CONDITIONS)) if AGES[i]>0]
    condition_young = [CONDITIONS[i] for i in range(len(CONDITIONS)) if AGES[i] == 0]

    if n_adults>0:
        average_condition_adult = sum(condition_adult) / n_adults
    else:
        average_condition_adult = -1

    if n_young>0:
        average_condition_young = sum(condition_young) / n_young
    else:
        average_condition_young = -1


    pre_season_population = len(CONDITIONS)
    young_ratio = AGES.count(0) / pre_season_population

    for i in range(len(CONDITIONS) - 1, -1, -1):
        resource_for_survival = RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0] if AGES[i] > 0 else RESOURCE_FOR_SURVIVAL_WINTER_YOUNG[0]
        resource_for_survival *= factor
        if CONDITIONS[i] < np.random.normal(resource_for_survival, RESOURCE_FOR_SURVIVAL_SD):

            if TO_COUNT_DATA[0]==True:  # for tuning parameters
                age_idx = 0 if AGES[i]>0 else 1
                TOTAL_DEATHS_ADULT_YOUNG[age_idx]+=1

            one_die(i)

    if TO_COUNT_DATA[0]:  # for tuning parameters
        if n_adults>0:
            survival_rate_adult = (len(AGES) - count(AGES, 0)) / n_adults
            SURVIVAL_RATES_WINTER_ADULT_YOUNG[0] += survival_rate_adult
        else:
            INVALID_YEARS["survival_rate_adult"]+=1
        if n_young>0:
            survival_rate_young = count(AGES, 0) / n_young
            SURVIVAL_RATES_WINTER_ADULT_YOUNG[1] += survival_rate_young
        else:
            INVALID_YEARS["survival_rate_young"]+=1


    for i in range(len(AGES)):
        AGES[i]+=1

    post_season_population = len(CONDITIONS)
    death_from_starvation = (pre_season_population-post_season_population)/pre_season_population

    return young_ratio, death_from_starvation, average_age_at_beginning_of_winter, average_condition_at_beginning_of_winter, average_condition_adult, average_condition_young


def one_year(food_factor = 1, unusual_death = None, resource_for_survival_factor = 1, annual_nesting_boxes_factor = 1):
    for i in range(len(CONDITIONS)):
        CONDITIONS[i]=0

    death_from_disease_all_spring, predation_all_spring, new_births_all_spring, unusual_dead, population_size_during_spring = spring(ANNUAl_FOOD[0]*food_factor, unusual_death, NESTIMG_BOXES*annual_nesting_boxes_factor)
    population_size_before_spring = population_size_during_spring[0]

    if len(CONDITIONS)==0:
        print("Extinction: spring", end=" ")
        return -1

    if TO_COUNT_DATA[0]:
        PROB_TO_BE_EATEN_ALL_YEARS.append(PROB_TO_BE_EATEN[0])

    population_size_before_winter = len(CONDITIONS)
    young_ratio, death_from_starvation, average_age_at_beginning_of_winter, average_condition_at_beginning_of_winter, average_condition_adult, average_condition_young = winter(resource_for_survival_factor)
    if len(CONDITIONS)==0:
        print("Extinction: winter", end=" ")
        return -1
    return death_from_disease_all_spring, predation_all_spring, new_births_all_spring, population_size_before_spring, population_size_before_winter, young_ratio, death_from_starvation, average_age_at_beginning_of_winter, average_condition_at_beginning_of_winter, average_condition_adult, average_condition_young, unusual_dead, population_size_during_spring


def multi_years(n_years, unusual_food = None, unusual_death = None, hard_winter = None, unusual_nesting_boxes = None, permanent_flag = False):
    # unusual_food = None or (year, factor)
    # unusual_death = None or (year, season_idx, death_ratio, p)
    #    year = int or "all"
    #    season_idx = int or "all"
    # hard_winter = None or (year, resource_for_survival_factor)
    # unusual_nesting_boxes = None or (year, nesting_boxes_factor)
    all_death_from_disease, all_predation_adults, all_predation_young, all_new_births, all_population_size_before_spring, all_population_size_before_winter, all_young_ratio, all_starvation, all_average_age, all_average_condition, all_condition_adult, all_condition_young, all_unusual_dead, all_population_size_during_spring = [], [], [], [], [], [], [], [], [], [], [], [], [], []
    for year in range(n_years):
        annual_food_factor = 1
        annual_unusual_death = None
        annual_resource_for_survival_factor = 1
        annual_nesting_boxes_factor = 1

        UNUSUAL_YEAR[0] = False

        if unusual_food and (year==unusual_food[0] or (permanent_flag and year>=unusual_food[0]) or unusual_food[0]=="all"):
            annual_food_factor = unusual_food[1]
            UNUSUAL_YEAR[0] = True
        if unusual_death and (unusual_death[0] in [year, "all"] or (permanent_flag and year>=unusual_death[0])):
            if random.random() < unusual_death[3]:
                annual_unusual_death = (unusual_death[1], unusual_death[2])
            UNUSUAL_YEAR[0] = True
        if hard_winter and (year==hard_winter[0] or (permanent_flag and year>=hard_winter[0])):
            annual_resource_for_survival_factor = hard_winter[1]
            UNUSUAL_YEAR[0] = True
        if unusual_nesting_boxes and (year==unusual_nesting_boxes[0] or (permanent_flag and year>=unusual_nesting_boxes[0])):
            annual_nesting_boxes_factor = unusual_nesting_boxes[1]
            UNUSUAL_YEAR[0] = True

        if year==YEAR_TO_START_COUNT: TO_COUNT_DATA[0]=True  # for tuning parameters

        one_year_result = one_year(annual_food_factor, annual_unusual_death, annual_resource_for_survival_factor, annual_nesting_boxes_factor)
        if one_year_result==-1:
            print("; year:", year)
            EXTINCTION.append(year)
            break

        death_from_disease, predation, new_births, population_size_before_spring, population_size_before_winter, young_ratio, starvation, average_age, average_condition, average_condition_adult, average_condition_young, unusual_dead, population_size_during_spring = one_year_result

        all_death_from_disease.append(death_from_disease)
        all_predation_adults.append(predation[0])
        all_predation_young.append(predation[1])
        all_new_births.append(new_births)
        all_population_size_before_spring.append(population_size_before_spring)
        all_population_size_before_winter.append(population_size_before_winter)
        all_young_ratio.append(young_ratio)
        all_starvation.append(starvation)
        all_average_age.append(average_age)
        all_average_condition.append(average_condition)
        all_unusual_dead.append(unusual_dead)
        all_population_size_during_spring.append(population_size_during_spring)

        if average_condition_young>=0:
            all_condition_young.append(average_condition_young)
        else:
            INVALID_YEARS["condition_young"].append(year)

        if average_condition_adult>=0:
            all_condition_adult.append(average_condition_adult)
        else:
            INVALID_YEARS["condition_adults"].append(year)

    return all_death_from_disease, all_predation_adults, all_predation_young, all_new_births, all_population_size_before_spring, all_population_size_before_winter, all_young_ratio, all_starvation, all_average_age, all_average_condition, all_condition_adult, all_condition_young, all_unusual_dead #, all_population_size_during_spring


def simulate_and_print(n_years, unusual_food = None, unusual_death = None, hard_winter = None, unusual_nesting_boxes = None, permanent_flag = False, folder=None, return_flag = False, txt_sub_folder=None, return_size_flag=False, return_average_flag=False, return_survival_and_brood_size_flag=False, remove_extinction = False):
    reset_globals()
    average_results_dict = dict()

    if txt_sub_folder:
        txt_folder = f"txt_files/{txt_sub_folder}"
    else:
        txt_folder = "txt_files"

    try:
        os.makedirs(txt_folder)
    except:
        pass

    all_death_from_disease, all_predation_adults, all_predation_young, all_new_births, all_population_size_before_spring, all_population_size_before_winter, all_young_ratio, all_starvation, all_average_age, all_average_condition, all_condition_adult, all_condition_young, all_unusual_dead = multi_years(n_years, unusual_food, unusual_death, hard_winter, unusual_nesting_boxes, permanent_flag)

    if len(EXTINCTION)>0:
        if remove_extinction:
            return -1
        n_years = EXTINCTION[0]

    births_by_seasons = all_new_births
    births = seasons_to_years(births_by_seasons)
    death_from_disease_by_seasons = all_death_from_disease
    death_from_disease = seasons_to_years(death_from_disease_by_seasons)
    births_per_bird = [births[i]/all_population_size_before_spring[i] for i in range(len(births))]

    relative_young_predation = proportion(all_predation_young, births)
    relative_adult_predation = proportion(all_predation_adults, all_population_size_before_spring)
    relative_death_from_disease = proportion(death_from_disease, sum_lists(all_population_size_before_spring, births))

    annual_x = list(range(n_years))
    seasonal_x = list(range(N_BREEDING_PERIODS))

    unusuals_dict = {"unusual food": unusual_food, "unusual death": unusual_death, "hard winter": hard_winter, "unusual nesting boxes": unusual_nesting_boxes}
    data_dict = {"Death from Disease": death_from_disease, "Predation Adults": all_predation_adults, "Predation Young": all_predation_young, "Hatchlings per Year": births, "Population Size Before Spring": all_population_size_before_spring, "Young Ratio": all_young_ratio, "Starvation": all_starvation, "Average Age at the Beginning of Winter": all_average_age, "Average Condition at the Beginning of Winter": all_average_condition, "Hatchlings by Periods": births_by_seasons, "Death from Disease by Periods": death_from_disease_by_seasons, "Hatchlings per Adult per Year": births_per_bird, "Average Condition Adult": all_condition_adult, "Average Condition Young": all_condition_young, "Predation Rate Young": relative_young_predation, "Predation Rate Adult": relative_adult_predation, "Death from Disease Rate": relative_death_from_disease}
    if unusual_death is not None:
        data_dict["unusual dead"] = all_unusual_dead

    # Check if there is unusual year, and take the first one
    single_unusual_year = None
    for unusual_parameter in unusuals_dict.keys():
        unusual_set = unusuals_dict[unusual_parameter]
        if unusual_set != None and type(unusual_set[0]) == int:
            single_unusual_year = unusual_set[0]

    for data_type in DATA_WITH_SEASONS:
            data = data_dict[data_type]
            new_data = average_lists(data[FIRST_YEARS_TO_IGNORE:]) if single_unusual_year is None else data[single_unusual_year]
            data_dict[data_type] = new_data

    if return_flag:
        for year in INVALID_YEARS["condition_young"]:
            data_dict["Average Condition Young"].insert(year, "invalid")
        return data_dict, all_population_size_before_winter

    if return_size_flag:
        counted_years = n_years - YEAR_TO_START_COUNT
        sum_population_spring = sum(data_dict["Population Size Before Spring"][YEAR_TO_START_COUNT:])
        return sum_population_spring/counted_years

    for data_type in data_dict.keys():
        data = data_dict[data_type]

        title = data_type
        if data_type not in DATA_WITH_SEASONS:
            title += f"\nmean = {round_for_model(average_for_model(data, FIRST_YEARS_TO_IGNORE))}"
            average_results_dict[data_type] = average_for_model(data, FIRST_YEARS_TO_IGNORE)
            f = open(f"{txt_folder}/{data_type}.txt", "a")
            f.write(f"{round_for_model(average_for_model(data, FIRST_YEARS_TO_IGNORE), MORE_TO_ROUND)}, ")
            f.close()
        if data_type == "Population Size Before Spring":
            title += f", {round_for_model(average_for_model(all_population_size_before_winter, FIRST_YEARS_TO_IGNORE))}"
            average_results_dict["Population Size Before Winter"] = average_for_model(all_population_size_before_winter,
                                                                                      FIRST_YEARS_TO_IGNORE)
            f = open(f"{txt_folder}/Population Size Before Winter.txt", "a")
            f.write(f"{round_for_model(average_for_model(all_population_size_before_winter, FIRST_YEARS_TO_IGNORE), MORE_TO_ROUND)}, ")
            f.close()
        if data_type == "Average Age at the Beginning of Winter":
            title += f", life expectancy: by winters = {round_for_model(TOTAL_AGE[0] / TOTAL_DEATHS[0])}, by springs = {round_for_model(TOTAL_AGE_BY_SPRINGS[0] / TOTAL_DEATHS[0], 1)}"

            average_results_dict["Life Expectancy by Winters"] = TOTAL_AGE[0] / TOTAL_DEATHS[0]
            average_results_dict["Life Expectancy by Springs"] = TOTAL_AGE_BY_SPRINGS[0] / TOTAL_DEATHS[0]

            f = open(f"{txt_folder}/Life Expectancy by Winters.txt", "a")
            f.write(f"{round_for_model(TOTAL_AGE[0]/TOTAL_DEATHS[0], MORE_TO_ROUND)}, ")
            f.close()
            f = open(f"{txt_folder}/Life Expectancy by Springs.txt", "a")
            f.write(f"{round_for_model(TOTAL_AGE_BY_SPRINGS[0]/TOTAL_DEATHS[0], MORE_TO_ROUND+1)}, ")
            f.close()

        X = seasonal_x if data_type in DATA_WITH_SEASONS else annual_x

        if return_average_flag:
            continue

        if data_type=="Average Condition young":
            X = [year for year in annual_x if year not in INVALID_YEARS["condition_young"]]

        if data_type=="Population Size Before Spring":
            label="before spring"
            plt.plot(X, all_population_size_before_winter, label="before winter")
        else:
            label=data_type.lower()

        plt.plot(X, data, label=label)

        for unusual_parameter in unusuals_dict.keys():
            unusual_set = unusuals_dict[unusual_parameter]
            if unusual_set==None:
                continue

            if type(unusual_set[0])==int and data_type not in DATA_WITH_SEASONS:
                x_unusual = unusual_set[0]
                if unusual_parameter=="unusual death":
                    x_unusual+= unusual_set[1] / N_BREEDING_PERIODS

                label = unusual_parameter + f": {unusual_set[-1]}"
                plt.axvline(x=x_unusual, color=COLOR_DICT[unusual_parameter], label=label, alpha=0.5)

        plt.title(title)
        plt.legend()
        plt.grid()

        # filename = data_type+" permanent change" if permanent_flag else data_type
        filename = data_type
        if folder is not None:
            path = f"graphs/{folder}"
            try:
                os.makedirs(path)
            except:
                pass
            filename = f"{path}/" + filename
        else:
            filename = "graphs/" + filename
        plt.savefig(filename)
        plt.clf()

    if return_average_flag:
        return average_results_dict

    counted_years = n_years - YEAR_TO_START_COUNT
    if return_survival_and_brood_size_flag:
        sr_adult = SURVIVAL_RATES_WINTER_ADULT_YOUNG[0] / counted_years
        sr_young = SURVIVAL_RATES_WINTER_ADULT_YOUNG[1] / (counted_years - INVALID_YEARS["survival_rate_young"])
        bs = BROOD_SIZE[0] / (counted_years-INVALID_YEARS["brood_size"])
        return sr_adult, sr_young, bs

    if len(EXTINCTION) > 0:
        return
    print("#####################\nfor tuning parameters\n#####################\n")
    sum_population_spring = sum(data_dict["Population Size Before Spring"][YEAR_TO_START_COUNT:])
    print("predation rate: adult =", PREDATION_ADULT_YOUNG[0] / TOTAL_DEATHS_ADULT_YOUNG[0], "; young =", PREDATION_ADULT_YOUNG[1] / TOTAL_DEATHS_ADULT_YOUNG[1])
    print("diseases in year: adult =", DISEASE_DEATH_ADULT_YOUNG[0] / sum_population_spring, "; young =", DISEASE_DEATH_ADULT_YOUNG[1] / sum(data_dict["Hatchlings per Year"][YEAR_TO_START_COUNT:]))
    print("average number of pairs: alive:", NUMBER_OF_PAIRS[0] / counted_years, "; dead:", NUMBER_OF_PAIRS[1] / counted_years)
    print("population size: adult =", POPULATION_SIZE_ADULT_YOUNG[0] / counted_years, "; young =", POPULATION_SIZE_ADULT_YOUNG[1] / counted_years, "; all =", sum(POPULATION_SIZE_ADULT_YOUNG) / counted_years)
    print("population size before spring =", sum_population_spring/counted_years)
    print("survival rates in winter: adult =", SURVIVAL_RATES_WINTER_ADULT_YOUNG[0] / counted_years, "; young =", SURVIVAL_RATES_WINTER_ADULT_YOUNG[1] / (counted_years - INVALID_YEARS["survival_rate_young"]))
    print("brood size:", BROOD_SIZE[0] / (counted_years-INVALID_YEARS["brood_size"]))
    print("prob to be eaten:", sum(PROB_TO_BE_EATEN_ALL_YEARS) / len(PROB_TO_BE_EATEN_ALL_YEARS))
    print("brood sizes histogram:", histogram_brood_size(BROOD_SIZES))


def multi_simulation(n_years, k_runs):
    results_dict = {output_key: [] for output_key in RELEVANT_OUTPUT_KEYS}
    for i in range(k_runs):
        results_one_simulation_dict = simulate_and_print(n_years, return_average_flag=True, remove_extinction=True)
        if results_one_simulation_dict==-1:     # Extinction
            for k in results_dict.keys():
                results_dict[k].append(None)
        else:
            for k in results_dict.keys():
                results_dict[k].append(results_one_simulation_dict[k])
    return results_dict

def serial_simulation(n_years, parameter, k_runs=1):
    results_dict = copy.deepcopy(BASIC_RESULTS_DICT) if parameter is not None else {output_key: [] for output_key in RELEVANT_OUTPUT_KEYS}

    parameters = {
        "maximum brood size": {"X": X_brood_size, "dict name": "results_brood_size_dict", "global": MAXIMUM_BROOD_SIZE},
        "partial brood limit": {"X": X_partial_brood_size, "dict name": "results_partial_brood_size_dict", "global": PARTIAL_BROOD_SIZE_LIMIT},
        "encounter probability": {"X": X_encounter_rate, "dict name": "results_encounter_rate_dict", "global": ENCOUNTER_PROBABILITY},
        "resource for winter": {"X": X_resource_threshold, "dict name": "results_resource_for_winter_dict", "global": RESOURCE_FOR_SURVIVAL_WINTER_ADULT},
        None: {"X": [0], "dict name": "base", "global": [None]}
    }

    print("RESOURCE_FOR_SURVIVAL_SD =", RESOURCE_FOR_SURVIVAL_SD)

    parameter_dict = parameters[parameter]
    if parameter in ["encounter probability", "resource for winter"]:
        initial_parameter = parameter_dict["global"][0]
    if parameter == "partial brood limit":
        PARTIAL_BROOD_SIZE_LIMIT[1]=0.3

    x_from = int(parameter is not None)
    print(parameter_dict["X"][x_from:])
    # [1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7]
    for x in parameter_dict["X"][x_from:]:
        parameter_dict["global"][0] = x
        if parameter in ["encounter probability", "resource for winter"]:
            parameter_dict["global"][0]*=initial_parameter
        if parameter=="resource for winter":
            RESOURCE_FOR_SURVIVAL_WINTER_YOUNG[0] = parameter_dict["global"][0]

        print("x =", parameter_dict["global"][0])

        results_one_simulation_dict = multi_simulation(n_years, k_runs)
        for k in results_dict.keys():
            results_dict[k].append(results_one_simulation_dict[k])

    filename = f"results {parameter}.txt"
    dict_name = parameter_dict['dict name']
    f = open(filename, "a")
    f.write(f"{dict_name} = " + "{\n")
    for k in results_dict.keys():
        f.write(f"\t\"{k}\": {results_dict[k]},\n")
    f.write("}")
    f.close()