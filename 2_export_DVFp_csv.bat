SETLOCAL ENABLEDELAYEDEXPANSION
SET PGPASSWORD=password
SET MYPATH=%~dp0
Rem give full control to the folder to all users
icacls "!MYPATH!tables" /grant "*S-1-1-0":(OI)(CI)F
FOR %%S IN (d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12, d13, d14,
			d15, d16, d17, d18, d19, d2a, d2b, d21, d22, d23, d24, d25, d26, d27,
			d28, d29, d30, d31, d32, d33, d34, d35, d36, d37, d38, d39, d40, d41,
			d42, d43, d44, d45, d46, d47, d48, d49, d50, d51, d52, d53, d54, d55,
			d56, d57, d58, d59, d60, d61, d62, d63, d64, d65, d66, d67, d68, d69,
			d70, d71, d72, d73, d74, d75, d76, d77, d78, d79, d80, d81, d82, d83,
			d84, d85, d86, d87, d88, d89, d90, d91, d92, d93, d94, d95,
			d971, d972, d973, d974) DO (
	 psql -U postgres -d dvf -f "!MYPATH!export.sql" -v schema="dvf_%%S" -v export_path="'!MYPATH!tables\%%S.csv'"
)
PAUSE