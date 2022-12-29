CREATE LOCAL TEMPORARY VIEW valid_mutations AS
(
    SELECT idmutation, datemut AS "date", valeurfonc AS "price"
    FROM dvf_d69.mutation
    WHERE (nblocmai + nblocapt <= 1)
);

CREATE LOCAL TEMPORARY VIEW adresse AS
(
    SELECT *
    FROM dvf_d69.adresse
);

CREATE LOCAL TEMPORARY VIEW habitations AS
(
    SELECT idmutation, libtyploc AS "housing_type",
        nbpprinc AS "n_rooms",
        sbati AS "housing_surface",
        ST_AsText(geomloc) AS "coordinates"
    FROM dvf_d69.local
    WHERE (codtyploc <=2) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
);

CREATE LOCAL TEMPORARY VIEW dependances AS
(
    SELECT MAX(idmutation), array_agg(sbati) AS "annexe_surfaces"
    FROM dvf_d69.local
    WHERE (codtyploc = 3) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW locaux_commerciaux AS
(
    SELECT idmutation, array_agg(sbati) AS "commercial_lot_surfaces"
    FROM dvf_d69.local
    WHERE (codtyploc = 4) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles AS
(
    SELECT idmutation,
        array_agg(dcntagri) AS "field_surfaces",
        array_agg(dcntsol) AS "ground_surfaces",
        array_agg(dcntnat) AS "nature_surfaces"
    FROM dvf_d69.disposition_parcelle
    WHERE (parcvendue) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW carrez AS
(
    SELECT idmutation, SUM(scarrez) AS "carrez_surface"
    FROM dvf_d69.lot
    WHERE idmutation IN (SELECT idmutation FROM valid_mutations)
    GROUP BY idmutation
)

-- COPY
-- (
--     SELECT * FROM valid_mutations
--     JOIN loc ON loc.idloc IN (SELECT idloc FROM valid_mutations)
-- )
-- TO 'C:\Users\Benoit\Documents\Project\DVFplus\tables\export.csv' (DELIMITER ',', FORMAT CSV, ENCODING 'UTF-8', HEADER)
-- ;