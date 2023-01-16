import zipfile
import pandas as pd
from io import BytesIO
import pathlib
import os

path = pathlib.Path(__file__).parent
ircom_path = path / "data" / "IRCOM"
tables_path = path / "export"

files = [file for file in os.listdir(ircom_path) if file.endswith(".zip")]
years = [f[-8:-4] for f in files]

def reshape_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df[["departement", "id_ville", "ville"]] = df[["departement", "id_ville", "ville"]].apply(lambda series: series.str.strip())
    piv = df.pivot_table(index=("departement", "id_ville", "ville"), columns="tranches", aggfunc='max')
    n_foyers_fiscaux = piv.n_foyers_fiscaux
    revenu_fiscal_total_keuros = piv.revenu_fiscal_total_keuros
    impot_total_keuros = piv.impot_total_keuros
    n_foyers_fiscaux.columns = n_foyers_fiscaux.columns.str.strip()
    revenu_fiscal_total_keuros.columns = revenu_fiscal_total_keuros.columns.str.strip()
    impot_total_keuros.columns = impot_total_keuros.columns.str.strip()
    column_names = {"TOTAL": "n_foyers_fiscaux",
                    "Total": "n_foyers_fiscaux",
                    '0 à 10 000': "n_foyers_0k_10k",
                    '10 001 à 12 000': "n_foyers_10k_12k",
                    '12 001 à 15 000': "n_foyers_12k_15k",
                    '15 001 à 20 000': "n_foyers_15k_20k",
                    '20 001 à 30 000' : "n_foyers_20k_30k",
                    '30 001 à 50 000': "n_foyers_30k_50k",
                    '50 001 à 100 000': "n_foyers_50k_100k",
                    'Plus de 100 000': "n_foyers_100k_plus",
                    "+ de 100 000": "n_foyers_100k_plus"}
    new = n_foyers_fiscaux.columns.difference(column_names.keys())
    if len(new) > 0:
        raise ValueError(f"Unexpected entries for column 'Nombre de foyers fiscaux': {new.to_list()}")
    keys = n_foyers_fiscaux.columns.intersection(column_names.keys())
    tranches = n_foyers_fiscaux[keys].rename(columns=column_names)
    tranches = tranches.apply(lambda series: pd.to_numeric(series, errors="coerce")).astype(pd.Int64Dtype()).reset_index()
    revenu_fiscal_total = pd.to_numeric(revenu_fiscal_total_keuros.rename(columns={"TOTAL": "Total"})["Total"], errors="coerce").to_numpy()
    impot_total = pd.to_numeric(impot_total_keuros.rename(columns={"TOTAL": "Total"})["Total"], errors="coerce").to_numpy()
    revenu_fiscal_moyen = pd.DataFrame(data=1000*revenu_fiscal_total/tranches.n_foyers_fiscaux.to_numpy(), columns=["revenu_fiscal_moyen"])
    montant_impot_moyen = pd.DataFrame(data=1000*impot_total/tranches.n_foyers_fiscaux.to_numpy(), columns=["montant_impot_moyen"])
    return pd.concat([tranches, revenu_fiscal_moyen, montant_impot_moyen], axis="columns")


columns={"Dép.": "departement", "Commune": "id_ville", "Libellé de la commune": "ville",
         "Revenu fiscal de référence par tranche (en euros)": "tranches",
         "Nombre de foyers fiscaux": "n_foyers_fiscaux",
         "Revenu fiscal de référence des foyers fiscaux": "revenu_fiscal_total_keuros",
         "Impôt net (total)*": "impot_total_keuros"}
df = pd.DataFrame()
for file, year in zip(files[::-1], years[::-1]):
    with zipfile.ZipFile(ircom_path / file, "r") as zf:
        file_bytes = zf.read(f"ircom_communes_complet_revenus_{year}.xlsx")
        header = pd.read_excel(BytesIO(file_bytes), nrows=100, usecols="C")
        h = list(header.iloc[:, 0]).index("Commune")
        sub = pd.read_excel(BytesIO(file_bytes), header=h+1, usecols="B:N", dtype={"Dép.": object, "Commune": object, "Libellé de la commune": object})
    sub.drop(index=sub[sub.Commune.isna()].index, inplace=True)
    sub = sub.rename(columns=columns)[list(columns.values())].replace("n.c.", float("nan"))
    sub = reshape_dataframe(sub)
    sub["date"] = year
    df = pd.concat([df, sub[["departement", "id_ville", "ville",
                             "n_foyers_fiscaux", "revenu_fiscal_moyen",
                             "montant_impot_moyen", "n_foyers_0k_10k",
                             "n_foyers_10k_12k", "n_foyers_12k_15k",
                             "n_foyers_15k_20k", "n_foyers_20k_30k",
                             "n_foyers_30k_50k", "n_foyers_50k_100k",
                             "n_foyers_100k_plus"]]])
    print(year)
df["revenu_fiscal_moyen"] = df.revenu_fiscal_moyen.astype(pd.Float64Dtype())
df["montant_impot_moyen"] = df.montant_impot_moyen.astype(pd.Float64Dtype())
df.round(decimals=2).to_csv(tables_path / "population.csv", index=False, float_format="%.2f")

if __name__ == "__main__":
    import IPython
    IPython.embed()