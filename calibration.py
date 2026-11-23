from simulation import *
# from potential_parameters import limited_parameters


def binary_search(low, high, target_pop_size, max_dev=10):
    mid = (low+high)/2
    if high-low<5:
        return mid
    try:
        ANNUAl_FOOD[0] = mid
        new_size = simulate_and_print(150, return_size_flag=True)
        if len(EXTINCTION)>0:
            new_size=0
    except:
        new_size = 0
    if abs(new_size-target_pop_size)<max_dev:
        print(ANNUAl_FOOD, RESOURCE_FOR_SURVIVAL_WINTER_ADULT, PROB_TO_STOP_NESTING[0], new_size)
        return mid
    if new_size<target_pop_size:
        return binary_search(mid, high, target_pop_size, max_dev)
    else:
        return binary_search(low, mid, target_pop_size, max_dev)


def validate_food_reproduction():
    X = []
    Y = []
    for i in range(11):
        factor = 10**(i/10)
        print(f"factor = {factor} [10^{i/10}]")
        mean_brood_size = multi_simulation(n_years=30, n_sim=350, unusual_food=(29,factor))
        X.append(i/10)
        Y.append(mean_brood_size)
    print(Y)
    plt.subplots_adjust(bottom=0.16)
    plt.tick_params(axis='both', labelsize=18)
    Y_rel = [y-Y[0] for y in Y]
    plt.plot(X, Y_rel, label="simulation")
    plt.plot(X, X, label="expected by literature")
    plt.xlabel("Change in food (factor = 10^x)", fontname='Times New Roman', fontsize=20, labelpad=10)
    plt.ylabel("Additional nestlings", fontname='Times New Roman', fontsize=20)
    plt.tight_layout()
    plt.legend()
    plt.grid()
    plt.savefig("validate food reproduction")
    plt.clf()


def validate_linear_function():

    def calc_res(thrshld, pstp):
        # P_start = 0.9
        # a1, b1, c1, d1 = 175919.74431818182, 4889.914772727273, 55473.82305194804, -5615.868506493506
        # a2, b2, c2, d2 = 200971875 / 1232, 5720625 / 1232, 112978125 / 616, -1940625 / 616

        # P_start = 0.5
        a1, b1, c1, d1 = 175908.0762987013, 4915.787337662337, 26024.756493506495, -4717.938311688312
        a2, b2, c2, d2 = 334375 / 2, 9375 / 2, 8718750 / 77, -187500 / 77

        # return a + b * thrshld + c * pstp + d * thrshld * pstp

        if pstp < 0.1:
            return a1 + b1 * thrshld + c1 * pstp + d1 * thrshld * pstp
        else:
            return a2 + b2 * thrshld + c2 * pstp + d2 * thrshld * pstp

    for sth in [8, 46, 85]:
      for pstp in [0.0, 0.05, 0.1, 0.15, 0.2]:
        RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0] = sth
        RESOURCE_FOR_SURVIVAL_WINTER_YOUNG[0] = sth
        PROB_TO_STOP_NESTING[0] = pstp
        ANNUAl_FOOD[0] = calc_res(sth, pstp)
        size = simulate_and_print(100, return_size_flag=True)
        print(f"{sth}, {pstp} -->", size)


def find_edge_values(threshold_values = (8, 85), p_stop_values = (0, 0.1, 0.2)):
    A = []
    for sth in threshold_values:
        for pstp in p_stop_values:
            RESOURCE_FOR_SURVIVAL_WINTER_ADULT[0] = sth
            RESOURCE_FOR_SURVIVAL_WINTER_YOUNG[0] = sth
            PROB_TO_STOP_NESTING[0] = pstp
            a = binary_search(190400, 600000, 240, 8)
            A.append(a)
            print(f"{sth}, {pstp} --> {a}")
    print([A[0], A[1], A[3], A[4]])
    print([A[1], A[2], A[4], A[5]])