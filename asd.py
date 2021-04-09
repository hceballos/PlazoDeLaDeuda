
import sqlite3
import numpy as np
import pandas as pd

cnx = sqlite3.connect('database.db')


# FECHA GENERACION
consultaServicioDeLaDeuda  = "\
	SELECT \
		servicioDeLaDeuda.id, \
		servicioDeLaDeuda.'Fecha Generación'\
	FROM  \
		servicioDeLaDeuda  \
	"
queryServicioDeLaDeuda = pd.read_sql_query(consultaServicioDeLaDeuda, cnx)

for index, row in queryServicioDeLaDeuda.iterrows():
	print("Processing... : ", row['id'], row['Fecha Generación']  )

	cnx.execute("""UPDATE
						contable
					SET
						Fecha= ?
					WHERE
						contable.id = ?
				""", (row['Fecha Generación'], row['id']) )
	cnx.commit()
print("Table updated...... ")


writer = pd.ExcelWriter('contable.xlsx', engine='xlsxwriter')
queryServicioDeLaDeuda.to_excel(writer, sheet_name='Todas las cuentas')
writer.save()



"""
consulta  = "\
	SELECT \
		contable.id, \
		contable.cuenta,\
		contable.Fecha,\
		contable.Saldo\
	FROM  \
		contable \
	WHERE \
		contable.cuenta = '21534'\
	"
query = pd.read_sql_query(consulta, cnx)
"""
