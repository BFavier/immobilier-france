import pandas as pd
import pathlib

path = pathlib.Path(__file__).parent
df = pd.read_excel(path / "data" / "LOVAC" / "logements-vacants-du-parc-prive-par-commune-au-01012020-lovac.xlsx",
                   usecols=["INSEE_COM", "NOM_COM", "CODE_DEPT", "Nb_log_pp_2020", "Nb_logvac_pp_010119",
                            "Nb_log_pp_2021", "Nb_logvac_pp_010120"],
                   sheet_name="Données")
columns = {"CODE_DEPT": "departement",
           "INSEE_COM": "id_ville",
           "NOM_COM": "ville"}
df.rename(columns=columns, inplace=True)
years = set(int(y[-2:]) for y in df.columns if y.startswith("Nb_log_pp_20") or y.startswith("Nb_logvac_pp_0101"))
concat = []
for year in years:
    cols = {f"{prefix}{year}": f"{renamed}"
            for prefix, renamed in [("Nb_log_pp_20", "n_logements"),
                                    ("Nb_logvac_pp_0101", "n_logements_vacants")]}
    sub_cols = [c for c in cols.keys() if c in df.columns]
    subset = df[list(columns.values()) + sub_cols].copy()
    for c in sub_cols:
        subset[c] = subset[c].astype(pd.Int64Dtype())
    subset.rename(columns=cols, inplace=True)
    subset["date"] = 2000 + year
    concat.append(subset)
new = pd.concat(concat)[["date", "departement", "id_ville", "ville", "n_logements", "n_logements_vacants"]]
new["id_ville"] = [n[-3:] for n in new["id_ville"]]
new.to_csv(path / "export" / "parc_immobilier.csv", index=False)

if __name__ == "__main__":
    import IPython
    IPython.embed()
