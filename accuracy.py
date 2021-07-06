"""
    This script calculates the accuracy for each of the predictions using
    three different methods. The description of the methods can be found in the
    paper. The accuracy for each of the positions is saved in separate files.
    The average accuracy for each of the methods is saved in the
    numeric_results text file.

    If you have any suggestions on how I can improve this code, feel free to
    open an issue on GitHub. I would love to hear your insight!
"""

import pandas as pd
import os
import numpy as np

predictions = pd.read_csv("results/predictions/predictions.csv", index_col=0)
OUTPUT_PATH = "results"
sx_differences = {}
fx_differences = {}
gx_differences = {}
for position in range(1, 21):
    # Contains differences between predicted position and actual position
    sx_differences[position] = []
    fx_differences[position] = []
    gx_differences[position] = []

if not os.path.isdir(f"{OUTPUT_PATH}/accuracy_files"):
    os.mkdir(f"{OUTPUT_PATH}/accuracy_files")

avg_diff_results = pd.DataFrame(columns=["position",  "s(x)_diff",
                                         "f(x)_diff", "g(x)_diff"])

correct_prob = pd.DataFrame(columns=["position", "s(x)_prob_finish",
                                     "s(x)_prob_no_finish",
                                     "f(x)_prob_finish",
                                     "f(x)_prob_no_finish",
                                     "g(x)_prob_finish",
                                     "g(x)_prob_no_finish"])

approx_results_prob = pd.DataFrame(columns=["position", "s(x)_prob_finish",
                                            "s(x)_prob_no_finish",
                                            "f(x)_prob_finish",
                                            "f(x)_prob_no_finish",
                                            "g(x)_prob_finish",
                                            "g(x)_prob_no_finish"])

for file in os.listdir("data/2019"):
    fp3_race = pd.read_csv(f"data/2019/{file}", index_col=0)
    fp3_results = fp3_race["fp3_pos"].values.tolist()
    race_results = fp3_race["race_pos"].values.tolist()
    for fp3_result, race_result in zip(fp3_results, race_results):
        # Getting the differences between predictions and actual race positions
        sx_differences[fp3_result].append(abs(fp3_result - race_result))
        fx_prediction = predictions.loc[fp3_result, "f(x)"]
        fx_differences[fp3_result].append(abs(fx_prediction - race_result))
        gx_prediction = predictions.loc[fp3_result, "g(x)"]
        gx_differences[fp3_result].append(abs(gx_prediction - race_result))

for position in range(1, 21):
    # Calculating average difference for each position
    sx_avg_diff = np.mean(sx_differences[position])
    fx_avg_diff = np.mean(fx_differences[position])
    gx_avg_diff = np.mean(gx_differences[position])
    avg_diff_row = [position, sx_avg_diff, fx_avg_diff, gx_avg_diff]
    avg_diff_results.loc[len(avg_diff_results)] = avg_diff_row

    # Calculating how many predictions were exactly correct
    sx_correct = sum(diff == 0 for diff in sx_differences[position])
    sx_correct_finish_prob = sx_correct / len(sx_differences[position])
    sx_correct_no_finish_prob = sx_correct / 21
    fx_correct = sum(diff == 0 for diff in fx_differences[position])
    fx_correct_finish_prob = fx_correct / len(fx_differences[position])
    fx_correct_no_finish_prob = fx_correct / 21
    gx_correct = sum(diff == 0 for diff in gx_differences[position])
    gx_correct_finish_prob = gx_correct / len(gx_differences[position])
    gx_correct_no_finish_prob = gx_correct / 21
    correct_row = [position, sx_correct_finish_prob, sx_correct_no_finish_prob,
                   fx_correct_finish_prob, fx_correct_no_finish_prob,
                   gx_correct_finish_prob, gx_correct_no_finish_prob]
    correct_prob.loc[len(correct_prob)] = correct_row

    # Calculating how many finishing positions were within 3 positions of
    # the assigned prediction
    sx_approx = sum(diff <= 3 for diff in sx_differences[position])
    sx_approx_finish_prob = sx_approx / len(sx_differences[position])
    sx_approx_no_finish_prob = sx_approx / 21

    fx_approx = sum(diff <= 3 for diff in fx_differences[position])
    fx_approx_finish_prob = fx_approx / len(fx_differences[position])
    fx_approx_no_finish_prob = fx_approx / 21

    gx_approx = sum(diff <= 3 for diff in gx_differences[position])
    gx_approx_finish_prob = gx_approx / len(gx_differences[position])
    gx_approx_no_finish_prob = gx_approx / 21

    approx_row = [position, sx_approx_finish_prob, sx_approx_no_finish_prob,
                  fx_approx_finish_prob, fx_approx_no_finish_prob,
                  gx_approx_finish_prob, gx_approx_no_finish_prob]

    approx_results_prob.loc[len(approx_results_prob)] = approx_row

# Saving the dataframes:
avg_diff_results.to_csv(f"{OUTPUT_PATH}/accuracy_files/avg_diff.csv",
                        index=False)

correct_prob.to_csv(f"{OUTPUT_PATH}/accuracy_files/corr_prob.csv", index=False)

approx_results_prob.to_csv(f"{OUTPUT_PATH}/accuracy_files/approx_prob.csv",
                           index=False)

if not os.path.exists(f"{OUTPUT_PATH}/numeric_results.txt"):
    with open(f"{OUTPUT_PATH}/numeric_results.txt", "w") as results_file:
        results_file.write("These are the results obtained during analysis:\n")

# Saving the average values:
with open(f"{OUTPUT_PATH}/numeric_results.txt", "a") as results_file:
    results_file.write("\n")
    results_file.write("Accuracy for Each Prediction:\n")
    results_file.write("s(x):\n")
    sx_avg_diff = avg_diff_results["s(x)_diff"].mean()
    sx_correct_finish_avg = correct_prob["s(x)_prob_finish"].mean()
    sx_correct_no_finish_avg = correct_prob["s(x)_prob_no_finish"].mean()
    sx_approx_finish_avg = approx_results_prob["s(x)_prob_finish"].mean()
    sx_approx_no_finish_avg = approx_results_prob["s(x)_prob_no_finish"].mean()
    results_file.write(f"- Avg. Difference: {sx_avg_diff}\n")
    results_file.write(f"""- Prob. Exactly Right: {sx_correct_finish_avg} &
{sx_correct_no_finish_avg} \n""")
    results_file.write(f"""- Prob. Approx Right: {sx_approx_finish_avg} &
{sx_approx_no_finish_avg} \n""")

    results_file.write("f(x):\n")
    fx_avg_diff = avg_diff_results["f(x)_diff"].mean()
    fx_correct_finish_avg = correct_prob["f(x)_prob_finish"].mean()
    fx_correct_no_finish_avg = correct_prob["f(x)_prob_no_finish"].mean()
    fx_approx_finish_avg = approx_results_prob["f(x)_prob_finish"].mean()
    fx_approx_no_finish_avg = approx_results_prob["f(x)_prob_no_finish"].mean()
    results_file.write(f"- Avg. Difference: {fx_avg_diff}\n")
    results_file.write(f"""- Prob. Exactly Right: {fx_correct_finish_avg} &
{fx_correct_no_finish_avg} \n""")
    results_file.write(f"""- Prob. Approx Right: {fx_approx_finish_avg} &
{fx_approx_no_finish_avg} \n""")

    results_file.write("g(x):\n")
    gx_avg_diff = avg_diff_results["g(x)_diff"].mean()
    gx_correct_finish_avg = correct_prob["g(x)_prob_finish"].mean()
    gx_correct_no_finish_avg = correct_prob["g(x)_prob_no_finish"].mean()
    gx_approx_finish_avg = approx_results_prob["g(x)_prob_finish"].mean()
    gx_approx_no_finish_avg = approx_results_prob["g(x)_prob_no_finish"].mean()
    results_file.write(f"- Avg. Difference: {gx_avg_diff}\n")
    results_file.write(f"""- Prob. Exactly Right: {gx_correct_finish_avg} &
{gx_correct_no_finish_avg} \n""")
    results_file.write(f"""- Prob. Approx Right: {gx_approx_finish_avg} &
{gx_approx_no_finish_avg} \n""")
    results_file.write("Obtained from accuracy.py \n")
