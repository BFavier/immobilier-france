import os
import pathlib
import datetime
import pandas as pd
import numpy as np


months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
month_mapping = {m: i for i, m in enumerate(months, start=1)}

def format_date(date: str) -> str:
    """
    format date from 'T3 2022' to '2022-09'
    """
    month, year = date.split(" ")
    year = int(year)
    month = month_mapping[month]
    day = (datetime.date(year + int(month/12), month%12+1, 1)-datetime.timedelta(days=1)).day
    return f"{year}-{month:02}-{day:02}"


path = pathlib.Path(__file__).parent
dataset_path = path / "data" / "taux_emprunts"
files = sorted((f for f in os.listdir(dataset_path) if f.endswith(".csv")), reverse=True)
df = pd.read_csv(dataset_path / files[-1], skiprows=6,
                 names=["date", "taux"],
                 sep=";", decimal=",", dtype={"date": object, "taux": float}, na_values=["-"]).dropna()
df["date"] = pd.to_datetime([format_date(d) for d in df["date"]], yearfirst=True)
df.to_csv(path / "export" / "taux_interet.csv", index=False)
