CREATE LOCAL TEMPORARY VIEW valid_mutations AS
(
    SELECT idmutation, vefa, datemut AS "transaction_date", valeurfonc AS "price"
    FROM :schema.mutation
    WHERE (nblocmai + nblocapt = 1)
);

CREATE LOCAL TEMPORARY VIEW adresse AS
(
    SELECT l.idmutation, a.commune AS "city", a.codepostal AS "zip_code",
        CONCAT(a.novoie, a.btq, ' ', a.typvoie, ' ', a.voie) AS "address"
    FROM :schema.adresse AS a, :schema.adresse_local AS al, :schema.local AS l
    WHERE (a.idadresse = al.idadresse) AND (al.iddispoloc = l.iddispoloc) AND (l.codtyploc <= 2)
);

CREATE LOCAL TEMPORARY VIEW habitations AS
(
    SELECT idmutation, iddispoloc,
        libtyploc AS "housing_type",
        nbpprinc AS "n_rooms",
        sbati AS "housing_surface",
        ST_AsText(geomloc) AS "coordinates"
    FROM :schema.local
    WHERE (codtyploc <=2) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
);

CREATE LOCAL TEMPORARY VIEW dependances AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(sbati) AS "annexe_surfaces"
    FROM :schema.local
    WHERE (codtyploc = 3) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW locaux_commerciaux AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(sbati) AS "commercial_lot_surfaces"
    FROM :schema.local
    WHERE (codtyploc = 4) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntagri) AS "field_surfaces",
        array_agg(dcntsol) AS "ground_surfaces",
        array_agg(dcntnat) AS "nature_surfaces"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) AND (idmutation IN (SELECT idmutation FROM valid_mutations))
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW carrez AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(scarrez) AS "carrez_surfaces"
    FROM :schema.lot
    WHERE idmutation IN (SELECT idmutation FROM valid_mutations)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW joined AS
(
    SELECT vm.transaction_date, vm.price, a.city, a.zip_code, a.address,
        h.housing_type, h.n_rooms, h.housing_surface, h.coordinates,
        d.annexe_surfaces, lc.commercial_lot_surfaces, p.field_surfaces,
        p.ground_surfaces, p.nature_surfaces, c.carrez_surfaces
    FROM valid_mutations AS vm
    LEFT JOIN adresse AS a
    ON vm.idmutation = a.idmutation
    LEFT JOIN habitations AS h
    ON vm.idmutation = h.idmutation
    LEFT JOIN dependances AS d
    ON vm.idmutation = d.idmutation
    LEFT JOIN locaux_commerciaux AS lc
    ON vm.idmutation = lc.idmutation
    LEFT JOIN parcelles AS p
    ON vm.idmutation = p.idmutation
    LEFT JOIN carrez AS c
    ON vm.idmutation = c.idmutation
);

COPY (SELECT * FROM joined) TO :export_path (DELIMITER ',', FORMAT CSV, ENCODING 'UTF-8', HEADER);