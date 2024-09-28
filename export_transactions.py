import pandas as pd
import numpy as np
import pathlib
import os

path = pathlib.Path(__file__).parent
tables_path = path / "export"
files = [f for f in os.listdir(tables_path) if f.startswith("d") and f.endswith(".csv") and f[1:-4].isnumeric()]
columns = ["id_transaction", "date_transaction", "prix", "departement", "id_ville", "ville",
           "code_postal", "adresse", "type_batiment", "vefa", "n_pieces",
           "surface_habitable",
           "id_parcelle_cadastre", "latitude", "longitude", "surface_dependances",
           "surface_locaux_industriels", "surface_terrains_agricoles",
           "surface_terrains_sols", "surface_terrains_nature"]
dtypes = [int, np.datetime64, float, str, int, str,
          int, str, str, bool, int,
          int,
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
df.drop(columns=["surface_habitable_carrez"], inplace=True)
df["vefa"] = (df["vefa"] == "t")
df["departement"] = [f"{d:02}" for d in df["departement"]]
arrays = {}
for c, t in zip(columns, dtypes):
    print(c, t)
    if t == str:
        arrays[c] = np.frombuffer(b"\x00".join(s.encode("utf-8") for s in df[c]), dtype=np.uint8)
    elif t == np.datetime64:
        arrays[c] = pd.to_datetime(df[c], format="%Y-%m-%d")
    else:
        arrays[c] = df[c].to_numpy(dtype=t)
# arrays = {c: np.frombuffer(b"\x00".join(s.encode("utf-8") for s in df[c]), dtype=np.uint8) if t == str
#              else pd.to_datetime(df[c], format="%Y-%m-%d") if t == np.datetime64
#              else df[c].to_numpy(dtype=t)
#              for c, t in zip(columns, dtypes)}
np.savez_compressed(tables_path / "transactions.npz", **arrays)
pd.DataFrame.from_dict({k: [s.decode("utf-8") for s in v.tobytes().split(b"\x00")] if v.dtype == np.uint8 else v for k, v in arrays.items()}
                       ).sample(n=100).to_csv(tables_path/"transactions_sample.csv", index=False)
