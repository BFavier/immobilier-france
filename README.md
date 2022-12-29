# DVFplus

This repository contains a set of scripts and instructions to export a subset of the DVF+ dataset.

The DVF+ dataset is an openly available SQL database that contains all real estate transactions in France, with some exceptions. It is a more complete version of the DVF dataset available [here](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/). The DVF+ dataset is hosted by the CEREMA at [this adress](https://datafoncier.cerema.fr/donnees/autres-donnees-foncieres/dvfplus-open-data).

## I) Install postgreSQL 11 and postGIS 3.2.3

Download the postgre SQL 11 installer for windows 64bits from the [enterprisedb website](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads). Set *password* as the admin password. At the end of the installation, add the path to the **psql** tool to the windows path.

~~~
setx /M PATH "%PATH%;C:\Program Files\PostgreSQL\11\bin"
~~~

Execute **stackbuilder** from the bin folder of postgreSQL installation folder. From the "Spatial Extensions" category, install the **PostGIS 3.2.3** extension.

## II) Create an empty database

To create an empty local database named **dvf** with postGIS extension activated, run the commands:

~~~
psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE dvf;"
psql -h localhost -p 5432 -U postgres -d dvf -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"
~~~

You can now visualize that the database exists by runing psql on the admin account which is named postgres by default. The admin password set during installation will be requested.

~~~
psql -U postgres
~~~

You can list the existing database with the *\l* command, connect to the *dvf* database with the *\c* command, and finally exit psql with the *\q* command.

~~~
\l
\c dvf
\q
~~~

## III) Import the SQL database dump

The latest version of the dump is available for download [here](https://cerema.app.box.com/v/dvfplus-opendata). The data to download is located in the *sql* folder, and then in the folder of the appropriate region name (or *National* for the whole country). The file might be cut in several parts that needs to be uncompressed using the [7zip](https://www.7-zip.org/download.html) tool. It should be uncompressed as a folder placed at the root of the repository. Its name should be similar to **DVFPlus_8-0_SQL_LAMB93_R084-ED222**, and it should contain a subfolder **1_DONNEES_LIVRAISON** containing sql files.

The only step needed to import the dump into the new database created earlier is to execute the **1_import_database.bat** script. Once the execution finished, the imported tables can be visualized with the following command lines:

~~~
psql -U postgres
~~~

And then inside of psql:

~~~
\c dvf
\dt *.*
~~~

## IV) Export the subset of the database

