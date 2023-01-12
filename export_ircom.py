import zipfile
import pandas as pd
from io import BytesIO
import pathlib
import os

path = pathlib.Path(__file__).parent
ircom_path = path / "IRCOM"
tables_path = path / "tables"

files = [file for file in os.listdir(ircom_path) if file.endswith(".zip")]
years = [f[-8:-4] for f in files]

def reshape_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    piv = df.pivot_table(index=("departement", "id_ville"), columns="tranches", aggfunc='max')
    tranches_columns = ['Total', '0 à 10 000', '10 001 à 12 000', '12 001 à 15 000',
       '15 001 à 20 000', '20 001 à 30 000', '30 001 à 50 000',
       '50 001 à 100 000']
    renamed_columns = ["n_foyers_fiscaux", "n_foyers_0k_10k", "n_foyers_10k_15k",
               "n_foyers_15k_20k", "n_foyers_20k_30k", "n_foyers_30k_50k",
               "n_foyers_50k_100k"]
    column_names = {t: r for t, r in zip(tranches_columns, renamed_columns)}
    tranches = piv.n_foyers_fiscaux[tranches_columns].rename(columns=column_names)
    revenu_fiscal_moyen = pd.DataFrame(data=1000*piv.revenu_fiscal_total_keuros[["Total"]]/tranches.n_foyers_fiscaux, columns=["revenu_fiscal_moyen"])
    revenu_net_moyen = pd.DataFrame(data=revenu_fiscal_moyen - 1000*piv.impot_total_keuros[["Total"]]/tranches.n_foyers_fiscaux, columns="revenu_net_moyen")
    return pd.concat([tranches, revenu_fiscal_moyen, revenu_net_moyen], axis="columns").reset_index()


columns={"Dép.": "departement", "Commune": "id_ville", "Libellé de la commune": "ville",
         "Revenu fiscal de référence par tranche (en euros)": "tranches",
         "Nombre de foyers fiscaux": "n_foyers_fiscaux",
         "Revenu fiscal de référence des foyers fiscaux": "revenu_fiscal_total_keuros",
         "Impôt net (total)*": "impot_total_keuros"}
df = pd.DataFrame()
for file, year in zip(files[::-1], years[::-1]):
    with zipfile.ZipFile(ircom_path / file, "r") as zf:
        file_bytes = zf.read(f"ircom_communes_complet_revenus_{year}.xlsx")
        header = pd.read_excel(BytesIO(file_bytes), nrows=1000, usecols="C")
        h = list(header.iloc[:, 0]).index("Commune")
        sub = pd.read_excel(BytesIO(file_bytes), header=h+1, usecols="B:N")
        sub.drop(index=sub[sub.Commune.isna()].index, inplace=True)
        sub = sub.rename(columns=columns)[list(columns.values())].replace("n.c.", float("nan"))
        sub = reshape_dataframe(sub)
        sub["date"] = year
        df = pd.concat([df, sub])
df.to_csv(tables_path / "revenus.csv", index=False)

if __name__ == "__main__":
    import IPython
    IPython.embed()