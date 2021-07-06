"""
    This script below calculates the necessary values to later calculate
    probabilities and assign predictions. The results are saved in the
    position_summary.csv file. I also calculate the Pearson Correlation between
    the FP3 position and its mean finishing position, and save the figure in
    the numeric_results text file.

    If you have any suggestions on how I can improve this code, feel free to
    open an issue on GitHub. I would love to hear your insight!
"""
import os
import pandas as pd
import numpy as np
from scipy import stats

INPUT_PATH = "data"
OUTPUT_PATH = "results"

# Dictionairy where we will store the data
data_dict = {}

result_columns = ["position", "mean_finish_position", "std_finish_position",
                  "race_amount", "cl_var_finish_position"]
summary_df = pd.DataFrame(columns=result_columns)

for position in range(1, 21):
    # The first item in the list will contain all of the finishing positions
    # The second item in the list will contain how many times the FP3 position
    # finished the race in 2019, since we do not consider the position
    # when the driver crashes or is disqualified.
    data_dict[position] = [[], 0]

for file in os.listdir(f"{INPUT_PATH}/2014-2018"):
    # Getting the finishing positions:
    fp3_race = pd.read_csv(f"{INPUT_PATH}/2014-2018/{file}", index_col=0)
    for fp3_pos, race_pos in zip(fp3_race["fp3_pos"].values,
                                 fp3_race["race_pos"].values):
        data_dict[fp3_pos][0].append(race_pos)

for file in os.listdir(f"{INPUT_PATH}/2019"):
    # Getting how many times the position finished in 2019
    fp3_race = pd.read_csv(f"{INPUT_PATH}/2019/{file}", index_col=0)
    for fp3_pos in fp3_race["fp3_pos"].values:
        data_dict[fp3_pos][1] += 1

for position, data in data_dict.items():
    # Calculating the data to be saved
    avg_race_position = np.mean(data[0])
    race_std = np.std(data[0])
    race_cl_var = race_std**2 / data[1]
    row = [position, avg_race_position, race_std, data[1], race_cl_var]
    summary_df.loc[len(summary_df)] = row

summary_df.to_csv(f"{OUTPUT_PATH}/position_summary.csv", index=False)

fp3_position_list = summary_df["position"].values.tolist()
avg_race_position = summary_df["mean_finish_position"].values.tolist()
corr, _ = stats.pearsonr(fp3_position_list, avg_race_position)

if not os.path.exists(f"{OUTPUT_PATH}/numeric_results.txt"):
    with open(f"{OUTPUT_PATH}/numeric_results.txt", "w") as results_file:
        results_file.write("These are the results obtained during analysis:\n")

with open(f"{OUTPUT_PATH}/numeric_results.txt", "a") as results_file:
    results_file.write("\n")
    results_file.write("FP3 Pos & Mean Race Pos Pearson Corr: " + str(corr))
    results_file.write("\n")
    results_file.write("Obtained from position_summary.py \n")
