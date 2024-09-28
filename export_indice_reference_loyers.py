import pathlib
import datetime
import pandas as pd

def format_date(date: str) -> str:
    """
    format date from '2022-T3' to '2022-09'
    """
    if not isinstance(date, str) or len(date) == 0:
        return "NaT"
    year, quarter = date.split("-")
    year = int(year)
    month = (int(quarter[1:])-1)*3
    return datetime.date(year + int(month/12), month%12+1, 1)
    return f"{year}-{month:02}"

path = pathlib.Path(__file__).parent
df = pd.read_csv(path / "data" / "Indice_de_Référence_des_Loyers" / "valeurs_trimestrielles.csv", sep=";", decimal=".", skiprows=4, names=["quarter", "IRL", "code", "date_publication"], parse_dates=["quarter"], date_parser=format_date)
df.dropna(subset=["IRL"], inplace=True)
# df["date"] = pd.to_datetime([format_date(d) for d in df["date"]], yearfirst=True)

df[["quarter", "IRL"]].to_csv(path / "export" / "indice_reference_loyers.csv", index=False)
