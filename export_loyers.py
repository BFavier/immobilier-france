import pandas as pd
import os
import pathlib

path = pathlib.Path(__file__).parent
data_path = path / "data"
concat = []
for year in os.listdir(data_path / "carte_loyers"):
    dir = data_path / "carte_loyers" / year
    files = {key: pd.read_csv(dir / next(iter(f for f in os.listdir(dir) if key in f and f.endswith(".csv"))),
                              sep=";", encoding="latin-1", decimal=",")
     for key in ["app", "mai"]}
    columns = {"DEP": "departement",
               "INSEE_C": "id_ville",
               "INSEE": "id_ville",
               "LIBGEO": "ville"}
    index = ["departement", "id_ville", "ville"]
    files["app"] = files["app"].rename(columns=columns).set_index(index)[["loypredm2"]].rename(columns={"loypredm2": "loyer_m2_appartement"})
    files["mai"] = files["mai"].rename(columns=columns).set_index(index)[["loypredm2"]].rename(columns={"loypredm2": "loyer_m2_maison"})
    sub = files["app"].join(files["mai"])
    sub["date"] = year
    concat.append(sub.reset_index(drop=False))
df = pd.concat(concat)[["departement", "id_ville", "ville", "date", "loyer_m2_appartement", "loyer_m2_maison"]]
df["id_ville"] = [str(id)[-3:] for id in df["id_ville"]]
df.sort_values(["date", "departement", "id_ville"]).to_csv(path / "export" / "loyers.csv", index=False)
