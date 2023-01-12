import pandas as pd
import numpy as np
import pathlib
import os

path = pathlib.Path(__file__).parent
tables_path = path / "tables"
# df = pd.read_csv(tables_path / "d01.csv")
files = [f for f in os.listdir(tables_path) if f.startswith("d") and f.endswith(".csv") and f[1:-4].isnumeric()]
columns = ["id_transaction", "date_transaction", "prix", "departement", "id_ville", "ville",
           "code_postal", "adresse", "type_batiment", "vefa", "n_pieces",
           "surface_habitable", "surface_habitable_carrez",
           "id_parcelle_cadastre", "latitude", "longitude", "surface_dependances",
           "surface_locaux_industriels", "surface_terrains_agricoles",
           "surface_terrains_sols", "surface_terrains_nature"]
dtypes = [int, np.datetime64, float, str, int, str,
          int, str, str, bool, int,
          int, str,
          str, float, float, str,
          str, str,
          str, str]

df_types = {c: t for c, t in zip(columns, dtypes)}
df = pd.DataFrame(columns=columns)
for file in files:
    sub = pd.read_csv(tables_path / file)
    df = pd.concat([df, sub])
    print(file)
df.dropna(axis="index", inplace=True)
arrays = {c: df[c].to_numpy() if t == str
             else pd.to_datetime(df[c], format="%Y-%m-%d") if t == np.datetime64
             else df[c].astype(t).to_numpy()
             for c, t in zip(columns, dtypes)}
np.savez_compressed(tables_path / "transactions.npz", **arrays)

if __name__ == "__main__":
    import IPython
    IPython.embed()