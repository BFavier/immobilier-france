SETLOCAL ENABLEDELAYEDEXPANSION
SET PGPASSWORD=password
SET MYPATH=%~dp0
Rem give full control to "tables" folder to all users
icacls "!MYPATH!tables" /grant "*S-1-1-0":(OI)(CI)F
FOR %%P IN (dvf_annexe dvf_d69) DO (
	SET TABLES=ann_cgi ann_nature_culture ann_nature_culture_speciale ann_nature_mutation ann_type_local ann_typologie
	IF %%P == dvf_d69 (
		SET TABLES=adresse adresse_dispoparc adresse_local  disposition disposition_parcelle local lot mutation mutation_article_cgi parcelle suf tmp_idmutation_doublon volume
	)
	FOR %%T IN (!TABLES!) DO (
		psql -h localhost -p 5432 -U postgres -d dvf -c "COPY %%P.%%T TO '%MYPATH%tables\%%T.csv' (DELIMITER ',', FORMAT CSV, ENCODING 'UTF-8', HEADER);"
	)
)