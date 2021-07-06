"""
    The script below calculates the Pearson Correlation between the FP3
    position and its corresponding race position. The correlation is calculated
    for each race and is saved into the pearson_corr_table.csv file. I also
    calcualate the average Pearson Correlation across all races and save it
    in the numeric_results text file.

    If you have any suggestions on how I can improve this code, feel free to
    open an issue on GitHub. I would love to hear your insight!
"""
import os
import pandas as pd
from scipy import stats
pearson_corr_df = pd.DataFrame(columns=["race_no",
                                        "pearson_corr",
                                        "p_value"])
INPUT_PATH = "data/2014-2018"
OUTPUT_PATH = "results"

for file_name in os.listdir(f"{INPUT_PATH}"):
    fp3_race = pd.read_csv(f"{INPUT_PATH}/{file_name}", index_col=0)
    fp3_positions = fp3_race["fp3_pos"].tolist()
    race_positions = fp3_race["race_pos"].tolist()
    r, p = stats.pearsonr(fp3_positions, race_positions)
    # int(file_name[:-4]) gets the race number
    pearson_corr_df.loc[len(pearson_corr_df)] = [int(file_name[:-4]), r, p]

pearson_corr_df.sort_values("race_no", inplace=True)
pearson_corr_df.to_csv(f"{OUTPUT_PATH}/pearson_corr_table.csv", index=False)

average_corr = pearson_corr_df["pearson_corr"].mean()

if not os.path.exists(f"{OUTPUT_PATH}/numeric_results.txt"):
    with open(f"{OUTPUT_PATH}/numeric_results.txt", "w") as results_file:
        results_file.write("These are the results obtained during analysis:\n")

with open(f"{OUTPUT_PATH}/numeric_results.txt", "a") as results_file:
    results_file.write("\n\n")
    results_file.write("FP3 Pos & Race Pos Pearson Corr: " + str(average_corr))
    results_file.write("\n")
    results_file.write("Obtained from pearson_correlation.py")
