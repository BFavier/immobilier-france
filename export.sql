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
    SELECT idmutation, iddispoloc, idpar AS "cadastre_id",
        libtyploc AS "housing_type",
        nbpprinc AS "n_rooms",
        sbati AS "housing_surface",
        ST_Transform(geomloc, 4326) AS "coordinates"
    FROM :schema.local
    WHERE (codtyploc <=2)
);

CREATE LOCAL TEMPORARY VIEW dependances AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(sbati) AS "annexe_surfaces"
    FROM :schema.local
    WHERE (codtyploc = 3) -- AND (sbati IS NOT NULL) AND (sbati > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW locaux_commerciaux AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(sbati) AS "commercial_lot_surfaces"
    FROM :schema.local
    WHERE (codtyploc = 4) -- AND (sbati IS NOT NULL) AND (sbati > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles_agr AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntagri) AS "field_surfaces"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) -- and (dcntagri IS NOT NULL) and (dcntagri > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles_sol AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntsol) AS "ground_surfaces"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) -- and (dcntsol IS NOT NULL) and (dcntsol > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles_nat AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntnat) AS "nature_surfaces"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) -- and (dcntnat IS NOT NULL) and (dcntnat > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW unique_lots AS
(
    SELECT MAX(idmutation) AS "idmutation", MAX(nolot) AS "nolot", MAX(scarrez) AS "scarrez"
    FROM :schema.lot
    GROUP BY (idmutation, nolot)
);

CREATE LOCAL TEMPORARY VIEW carrez AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(scarrez) AS "carrez_surfaces"
    FROM unique_lots
    WHERE (scarrez IS NOT NULL) AND (scarrez > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW joined AS
(
    SELECT vm.idmutation AS "transaction_id",
        vm.transaction_date, vm.price, a.city, a.zip_code, a.address,
        h.housing_type, h.n_rooms, h.housing_surface, h.cadastre_id,
        ST_Y(h.coordinates) AS "latitude", ST_X(h.coordinates) AS "longitude",
        d.annexe_surfaces, lc.commercial_lot_surfaces, p_agr.field_surfaces,
        p_sol.ground_surfaces, p_nat.nature_surfaces, c.carrez_surfaces
    FROM valid_mutations AS vm
    LEFT JOIN adresse AS a
    ON vm.idmutation = a.idmutation
    LEFT JOIN habitations AS h
    ON vm.idmutation = h.idmutation
    LEFT JOIN dependances AS d
    ON vm.idmutation = d.idmutation
    LEFT JOIN locaux_commerciaux AS lc
    ON vm.idmutation = lc.idmutation
    LEFT JOIN parcelles_agr AS p_agr
    ON vm.idmutation = p_agr.idmutation
    LEFT JOIN parcelles_sol AS p_sol
    ON vm.idmutation = p_sol.idmutation
    LEFT JOIN parcelles_nat AS p_nat
    ON vm.idmutation = p_nat.idmutation
    LEFT JOIN carrez AS c
    ON vm.idmutation = c.idmutation
    ORDER BY vm.transaction_date
);

COPY (SELECT * FROM joined) TO :export_path (DELIMITER ',', FORMAT CSV, ENCODING 'UTF-8', HEADER);