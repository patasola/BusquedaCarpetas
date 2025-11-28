import pyodbc
print("Drivers ODBC detectados:")
for driver in pyodbc.drivers():
    print(f" - {driver}")
