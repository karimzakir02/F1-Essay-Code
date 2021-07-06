"""
    The script below assigns predictions based on the probability in the
    results/probabilities_positions directory. The predictions are assigned
    using three methods, denoted as s(x), f(x), and g(x). You can find the
    descriptions for each of the methods in the paper.

    If you have any suggestions on how I can improve this code, feel free to
    open an issue on GitHub. I would love to hear your insight!
"""
import pandas as pd
import os

INPUT_PATH = "results/probabilities_positions"
predictions_df = pd.DataFrame(columns=["position", "s(x)", "f(x)", "g(x)"])
OUTPUT_PATH = "results"

if not os.path.isdir(f"{OUTPUT_PATH}/predictions"):
    os.mkdir(f"{OUTPUT_PATH}/predictions")

available_positions = list(range(1, 21))
fx_predictions = []

for race_pos in range(1, 21):
    # Getting f(x) predictions
    maximum_probability = 0
    best_position = 0

    # Calculating which available fp3 position is the likeliest to finish
    # in race_pos
    for fp3_pos in available_positions:
        probabilities_df = pd.read_csv(f"{INPUT_PATH}/{fp3_pos}.0.csv")
        pos_df = probabilities_df[probabilities_df["position"] == race_pos]
        probability = pos_df["probability"].values.tolist()[0]
        if probability > maximum_probability:
            maximum_probability = probability
            best_position = fp3_pos

    available_positions.remove(best_position)
    fx_predictions.append(best_position)

gx_predictions = []

for fp3_position in range(1, 21):
    # Getting g(x) predictions
    probabilities_df = pd.read_csv(f"{INPUT_PATH}/{fp3_position}.0.csv",
                                   index_col=0)
    probabilities = probabilities_df["probability"].values.tolist()
    highest_probability = max(probabilities)
    gx_prediction = probabilities.index(highest_probability) + 1
    gx_predictions.append(gx_prediction)


for sx, fx, gx in zip(range(1, 21), fx_predictions, gx_predictions):
    # Populating the dataframe for each position
    predictions_df.loc[len(predictions_df)] = [sx, sx, fx, gx]

predictions_df.to_csv(f"{OUTPUT_PATH}/predictions/predictions.csv",
                      index=False)
