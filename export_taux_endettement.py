import pandas as pd
import pathlib
import re

path = pathlib.Path(__file__).parent
df = pd.read_csv(path / "data" / "TEC00104" / "tec00104.tsv", sep="(?: *\t)|,", engine='python')
df.drop(columns={"unit","sector","na_item"}, inplace=True)
df.set_index(r"geo\time", inplace=True)
df = df.loc["FR", :].apply(lambda x: float(re.sub("[^0-9.]", "", str(x)))).to_frame("taux_endettement")
df.index.rename("date", inplace=True)
df.reset_index(drop=False, inplace=True)
df["date"] = df["date"].astype(int)
df.to_csv(path / "export" / "taux_endettement.csv", index=False)
