import os
import pathlib
import pandas as pd

path = pathlib.Path(__file__).parent
dataset_path = path / "data" / "flux_nouveaux_emprunts_immobiliers"
files = sorted((f for f in os.listdir(dataset_path) if f.endswith(".csv")), reverse=True)
df = pd.read_csv(dataset_path / files[-1],
                 sep=";", decimal=".", dtype={"obs_value": int}).dropna(subset=["obs_value"])
df.rename(columns={"time_period": "date", "obs_value": "emprunts_M€"})[["date", "emprunts_M€"]].to_csv(path / "export" / "flux_nouveaux_emprunts.csv", index=False)
