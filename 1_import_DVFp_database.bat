SET PGPASSWORD=password
psql -h localhost -p 5432 -U postgres -c "DROP DATABASE dvf;
psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE dvf;"
psql -h localhost -p 5432 -U postgres -d dvf -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"
psql -h localhost -p 5432 -U postgres -d dvf -f "./DVFPlus_8-0_SQL_LAMB93_RNational-ED222/1_DONNEES_LIVRAISON/dvf_initial.sql"
psql -h localhost -p 5432 -U postgres -d dvf -f "./DVFPlus_8-0_SQL_LAMB93_RNational-ED222/1_DONNEES_LIVRAISON/dvf_departements.sql"
pause