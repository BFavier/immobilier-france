import os
import pathlib
import pandas as pd

path = pathlib.Path(__file__).parent
dataset_path = path / "data" / "taux_emprunts"
files = sorted((f for f in os.listdir(dataset_path) if f.endswith(".csv")), reverse=True)
df = pd.read_csv(dataset_path / files[-1],
                 sep=";", decimal=".").dropna(subset=["obs_value"])
df.rename(columns={"time_period": "date", "obs_value": "taux"})[["date", "taux"]].to_csv(path / "export" / "taux_interet.csv", index=False)
