"""
    This script calculates the probability of an FP3 position finishing in
    different race positions using the Central Limit Theorem. The probabilities
    are first calculated using z-score increments and saved in the
    probabilities_increments directory; the data there will be used to plot
    the probability curve. Afterwards, the probabilities are calculated for
    each finishing position individually and are saved in the
    probabilities_positions directory; this data is used to make the
    predictions.

    If you have any suggestions on how I can improve this code, feel free to
    open an issue on GitHub. I would love to hear your insight!
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

INPUT_PATH = "results"
OUTPUT_PATH = "results"
position_data = pd.read_csv(f"{INPUT_PATH}/position_summary.csv", index_col=0)
# Getting the z-score increments:
increments = np.arange(-3.0, 3.1, 0.1)

if not os.path.isdir(f"{OUTPUT_PATH}/probabilities_increments"):
    os.mkdir(f"{OUTPUT_PATH}/probabilities_increments")

if not os.path.isdir(f"{OUTPUT_PATH}/probabilities_positions"):
    os.mkdir(f"{OUTPUT_PATH}/probabilities_positions")

for pos in position_data.index:
    increment_result = pd.DataFrame(columns=["std_increments", "aprox_pos",
                                             "probability"])
    pos_result = pd.DataFrame(columns=["position", "probability"])
    pos_row = position_data.loc[pos]
    mean_finish = pos_row["mean_finish_position"]
    cl_var = pos_row["cl_var_finish_position"]
    # Getting predictions for z-score increments
    for increment in increments:
        increment_pos = mean_finish + increment * cl_var
        increment_prob = stats.norm(mean_finish, cl_var).pdf(increment_pos)
        increment_row = [increment, increment_pos, increment_prob]
        increment_result.loc[len(increment_result)] = increment_row
    increment_result.to_csv(f"{INPUT_PATH}/probabilities_increments/{pos}.csv",
                            index=False)

    # Getting predictions for each position
    for pos_race in position_data.index:
        pos_prob = stats.norm(mean_finish, cl_var).pdf(pos_race)
        pos_row = [pos_race, pos_prob]
        pos_result.loc[len(pos_result)] = pos_row
    pos_result.to_csv(f"results/probabilities_positions/{pos}.csv",
                      index=False)
