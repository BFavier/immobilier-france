import os
import pathlib
import datetime
import pandas as pd
import numpy as np


def format_date(date: str) -> str:
    """
    fromat date from 'T3 2022' to '2022-09'
    """
              
    months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    month, year = date.split(" ")
    year = int(year)
    month = months.index(month) + 1
    day = (datetime.date(year + int(month/12), month%12+1, 1)-datetime.timedelta(days=1)).day
    return f"{year}-{month:02}-{day:02}"


path = pathlib.Path(__file__).parent
dataset_path = path / "data" / "flux_nouveaux_emprunts_immobiliers"
files = sorted((f for f in os.listdir(dataset_path) if f.endswith(".csv")), reverse=True)
df = pd.read_csv(dataset_path / files[-1], skiprows=5,
                 names=["date", "emprunts_M€"],
                 sep=";", decimal=",")
df["date"] = pd.to_datetime([format_date(d) for d in df["date"]], yearfirst=True)
df.to_csv(path / "export" / "flux_nouveaux_emprunts.csv", index=False)