from util import *
import numpy as np

from results.results_brood_size import results_brood_size_dict, X_brood_size, labels_brood_size
from results.results_encounter_rate import results_encounter_rate_dict, X_encounter_rate, labels_encounter_rate
from results.results_partial_brood_limit import results_partial_brood_size_dict, X_partial_brood_size, labels_partial_brood_size
from results.results_resource_threshold import results_resource_for_winter_dict, X_resource_threshold, labels_resource_threshold

from results.results_brood_size_high_var import results_brood_size_dict as results_brood_size_dict_288
from results.results_encounter_rate_high_var import results_encounter_rate_dict as results_encounter_rate_dict_288, X_encounter_rate as X_encounter_rate_288
from results.results_partial_brood_limit_high_var import results_partial_brood_size_dict as results_partial_brood_size_dict_288
from results.results_resource_threshold_high_var import results_resource_for_winter_dict as results_resource_threshold_288

import matplotlib.pyplot as plt

def print_results(experiment, increase_size=False, high_sig_flag_list = [False], name_by_index = False):


    if experiment=="brood size":
        data_dicts = results_brood_size_dict, results_brood_size_dict_288
        X = X_brood_size
        xlabel = "Maximum brood size"
        experiment_index = 1
    elif experiment=="partial brood size":
        data_dicts = results_partial_brood_size_dict, results_partial_brood_size_dict_288
        X = X_partial_brood_size
        xlabel = "Especially brood limit"
        experiment_index = 3
    elif experiment=="encounter probability":
        data_dicts = results_encounter_rate_dict, results_encounter_rate_dict_288
        X = X_encounter_rate
        xlabel = "x (Encounter probability factor)"
        experiment_index = 5
    elif experiment == "resource threshold":
        data_dicts = results_resource_for_winter_dict, results_resource_threshold_288
        X = X_resource_threshold
        xlabel = "x (Mean survival threshold factor)"
        experiment_index = 7
    else:
        return

    data_types = list(data_dicts[0].keys())
    add_to_experiment_index = 0
    for data_type in data_types:
        contraction = 0.9
        fig, ax = plt.subplots(figsize=(7 * contraction, 4.8 * contraction))
        if data_type in ["Life Expectancy by Winters", "Life Expectancy by Springs", "Hatchlings per Adult per Year",
                         "Young Ratio"] and increase_size:
            fig.set_size_inches(7, 4.8)
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.3f}"))

        if data_type == "Population Size Before Winter" and experiment == "partial brood size":
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.1f}"))

        add_to_file_name = ""

        for high_sig_flag in high_sig_flag_list:    # 0: low sigma; 1: high sigma

            if data_type=="population size during spring":
                continue

            data_dict = data_dicts[int(high_sig_flag)]
            data = data_dict[data_type]

            color = default_color
            if high_sig_flag:
                color = "blue"

            filtered = [(x, values) for x, values in zip(X, data)
                        if None not in values]

            X_filtered = [x for x, values in filtered]
            data_filtered = [values for x, values in filtered]

            means = [np.mean(values) for values in data_filtered]
            sds = [np.std(values) for values in data_filtered]

            plt.errorbar(
                X_filtered, means,
                yerr=sds,
                fmt='o',
                color=color,
                markersize=6,
                capsize=5,
                capthick=1.5
            )

            if high_sig_flag:
                add_to_file_name += " high sig"
                add_to_experiment_index=1
            else:
                add_to_file_name += " low sig"

        parameter_index = DATA_TYPES.index(data_type)+1

        plt.grid()
        plt.subplots_adjust(bottom=0.16)
        plt.tight_layout()
        plt.tick_params(axis='both', labelsize=18)

        plt.xlabel(xlabel, fontname='Times New Roman', fontsize=default_font_size, labelpad=10)
        y_label = data_type.capitalize()
        if y_label=="Starvation":
            y_label+= " rate"
        if y_label == "Average condition at the beginning of winter":
            y_label = "Body condition"

        y_fontsize = 21 if data_type in ["Hatchlings per Adult per Year", "Population Size Before Spring", "Population Size Before Winter"] else default_font_size
        plt.ylabel(y_label, fontsize=y_fontsize, fontname='Times New Roman')
        if name_by_index:
            filename=f"fig{experiment_index+add_to_experiment_index}_{parameter_index}.png"
        else:
            filename = f"{experiment} - {data_type}; {add_to_file_name}.png"
        plt.tight_layout()

        plt.savefig("graphs/"+filename)
        plt.clf()


def plot_none_percentage(L, X, X_label):
    percentages = [
        100 * sum(x is None for x in sublist) / len(sublist)
        if sublist else 0
        for sublist in L
    ]

    contraction = 0.9
    fig, ax = plt.subplots(figsize=(7 * contraction, 4.8 * contraction))
    plt.plot(X, percentages, marker='o', color = (0.5,0,1))
    plt.xlabel(X_label)
    plt.ylabel("Extinction rate (%)")
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig("graphs/" + X_label)
    plt.clf()


for high_sig in [True, False]:
    for experiment_name in ["brood size", "partial brood size", "encounter probability", "resource threshold"]:
        print_results(experiment=experiment_name, increase_size=False, high_sig_flag_list=[high_sig], name_by_index=True)


plot_none_percentage(list(results_encounter_rate_dict.values())[0], X_encounter_rate, "x (Encounter probability factor)")