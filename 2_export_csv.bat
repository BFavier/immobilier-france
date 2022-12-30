SETLOCAL ENABLEDELAYEDEXPANSION
SET PGPASSWORD=password
SET MYPATH=%~dp0
Rem give full control to the folder to all users
icacls "!MYPATH!tables" /grant "*S-1-1-0":(OI)(CI)F
FOR %%S IN (dvf_d69) DO (
	 psql -U postgres -d dvf -f "!MYPATH!export.sql" -v schema="%%S" -v export_path="'!MYPATH!tables\export.csv'"
)
PAUSE