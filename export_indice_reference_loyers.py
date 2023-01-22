import pathlib
import datetime
import pandas as pd

def format_date(date: str) -> str:
    """
    fromat date from '2022-T3' to '2022-09'
    """
    year, month = date.split("-")
    year = int(year)
    month = int(month[1:])*3
    day = (datetime.date(year + int(month/12), month%12+1, 1)-datetime.timedelta(days=1)).day
    return f"{year}-{month:02}-{day:02}"

path = pathlib.Path(__file__).parent
df = pd.read_csv(path / "data" / "Indice_de_Référence_des_Loyers" / "valeurs_trimestrielles.csv", sep=";", skiprows=3, names=["date", "IRL", "code", "date_parution"])
df.dropna(subset=["IRL"], inplace=True)
df["date"] = pd.to_datetime([format_date(d) for d in df["date"]], yearfirst=True)

df[["date", "IRL"]].to_csv(path / "export" / "indice_reference_loyers.csv", index=False)

if __name__ == "__main__":
    import IPython
    IPython.embed()
