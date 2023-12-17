import pathlib
import os
import pandas as pd

path = pathlib.Path(__file__).parent
data_path = path / "data" / "actifs_financiers"
files = sorted((f for f in os.listdir(data_path) if f.endswith(".csv") and f.startswith("DP_LIVE_")), reverse=True)
df = pd.read_csv(data_path / files[-1])
df = df[df["LOCATION"] == "FRA"]
df = df.drop(columns=[c for c in df.columns if c not in ("TIME", "SUBJECT", "Value")])
df = df.rename(columns={"TIME": "date"})
df = df.pivot(index="date", columns="SUBJECT", values="Value").reset_index(drop=False)
df.rename(columns={"CURDEP": "fraction_depot_banque",
                   "LIFEINSRSV": "fraction_assurance_vie",
                   "MFSH": "fraction_fonds_communs",
                   "PENSIONF": "fraction_fond_pension",
                   "SECOTHSH": "fraction_titres_non_action",
                   "SHOTHEQTY": "fraction_actions",
                   "TOT": "USD_par_habitant"},
          inplace=True)
fracs = [c for c in df.columns if c.startswith("fraction_")]
df[fracs] /= 100

change = pd.read_csv(data_path / "usd-eur.csv", decimal=",")
day, month, year = zip(*[tuple(int(v) for v in  d[:10].split("/")) for d in change["Date"]])
change["year"] = year
change = change[["Close", "year"]].groupby("year").agg("mean")["Close"].to_dict()

df["euros_par_habitant"] = [usd/change[year] for usd, year in zip(df["USD_par_habitant"], df["date"])]

df[["date", "USD_par_habitant", "euros_par_habitant"]+fracs].to_csv(path / "export" / "actifs_financiers.csv", index=False)

