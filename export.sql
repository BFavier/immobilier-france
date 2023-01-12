CREATE LOCAL TEMPORARY VIEW valid_mutations AS
(
    SELECT idmutation, vefa, datemut AS "date_transaction", valeurfonc AS "prix"
    FROM :schema.mutation
    WHERE (nblocmai + nblocapt = 1)
);

CREATE LOCAL TEMPORARY VIEW adresse AS
(
    SELECT l.idmutation, a.commune AS "ville", a.codepostal AS "departement",
        CONCAT(a.novoie, a.btq, ' ', a.typvoie, ' ', a.voie) AS "adresse",
        p.codcomm AS "id_ville"
    FROM :schema.adresse AS a, :schema.adresse_local AS al, :schema.local AS l, :schema.parcelle AS p
    WHERE (l.codtyploc <= 2) AND (a.idadresse = al.idadresse) AND (al.iddispoloc = l.iddispoloc) AND (p.idpar = l.idpar)
);

CREATE LOCAL TEMPORARY VIEW habitations AS
(
    SELECT idmutation, iddispoloc, idpar AS "id_parcelle_cadastre",
        libtyploc AS "type_batiment",
        nbpprinc AS "n_pieces",
        sbati AS "surface_habitable",
        ST_Transform(geomloc, 4326) AS "coordinates"
    FROM :schema.local
    WHERE (codtyploc <=2)
);

CREATE LOCAL TEMPORARY VIEW dependances AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(sbati) AS "surface_dependances"
    FROM :schema.local
    WHERE (codtyploc = 3)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW locaux_commerciaux AS
(
    SELECT MAX(idmutation) AS "idmutation", array_agg(sbati) AS "surface_locaux_industriels"
    FROM :schema.local
    WHERE (codtyploc = 4)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles_agr AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntagri) AS "surface_terrains_agricoles"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) and (dcntagri IS NOT NULL) and (dcntagri > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles_sol AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntsol) AS "surface_terrains_sols"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) and (dcntsol IS NOT NULL) and (dcntsol > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW parcelles_nat AS
(
    SELECT MAX(idmutation) AS "idmutation",
        array_agg(dcntnat) AS "surface_terrains_nature"
    FROM :schema.disposition_parcelle
    WHERE (parcvendue) and (dcntnat IS NOT NULL) and (dcntnat > 0)
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
    SELECT MAX(idmutation) AS "idmutation", array_agg(scarrez) AS "surface_habitable_carrez"
    FROM unique_lots
    WHERE (scarrez IS NOT NULL) AND (scarrez > 0)
    GROUP BY idmutation
);

CREATE LOCAL TEMPORARY VIEW joined AS
(
    SELECT vm.idmutation AS "id_transaction",
        vm.date_transaction, vm.prix, a.id_ville, a.ville, a.departement, a.adresse,
        h.type_batiment, vm.vefa, h.n_pieces, h.surface_habitable, c.surface_habitable_carrez, h.id_parcelle_cadastre,
        ST_Y(h.coordinates) AS "latitude", ST_X(h.coordinates) AS "longitude",
        d.surface_dependances, lc.surface_locaux_industriels, p_agr.surface_terrains_agricoles,
        p_sol.surface_terrains_sols, p_nat.surface_terrains_nature
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
    ORDER BY vm.date_transaction
);

COPY (SELECT * FROM joined) TO :export_path (DELIMITER ',', FORMAT CSV, ENCODING 'UTF-8', HEADER);