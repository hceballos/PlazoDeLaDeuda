import sqlalchemy
import pandas as pd
import glob
import sqlite3
import numpy as np
from datetime import datetime


class Database():

	def __init__(self):

		self.parseCarteraFinancieraContable()

	def parseCarteraFinancieraContable(self):
		contable = pd.DataFrame()
		# Cartera Financiera Contable: cuentas 21522, 21529, 21534
		for f in glob.glob('CarteraFinancieraContable/*.xls', recursive=True):
			df = pd.read_excel(f) 
			df = df.drop(df.index[range(10)])
			print('Procesando  : ', f)
			contable = contable.append(df,ignore_index=True)

		contable.rename(columns={'Cartera Financiera Contable.': 'Cuenta Contable', 'Unnamed: 1': 'Principal', 'Unnamed: 2': 'Saldo', 'Unnamed: 3': 'Tipo Movimiento', 'Unnamed: 4': 'Fecha', 'Unnamed: 5': 'Folio','Unnamed: 6': 'Título','Unnamed: 7': 'Debe', 'Unnamed: 8': 'Haber', 'Unnamed: 9': 'Saldo Acumulado', 'Unnamed: 10': 'Tipo Documento', 'Unnamed: 11': 'Número'}, inplace=True) 
		contable['Título']	= contable.drop( contable[ contable['Título'] == 'Total Flujos Periodo' ].index , inplace=True )
		contable['Fecha']	= pd.to_datetime(contable['Fecha']).dt.date
		contable['Rut']		= contable['Principal'].str.split(' ', n = 1, expand = True)[0]
		contable['cuenta']	= contable['Cuenta Contable'].str.split(' ', n = 1, expand = True)[0]
		contable['Saldo']	= contable['Haber'] - contable['Debe']
		contable['id']		= contable['Rut'] + contable['Número']




		"""
		del contable['Principal']
		del contable['Tipo Movimiento']
		del contable['Folio']
		del contable['Título']
		del contable['Saldo Acumulado']
		del contable['Tipo Documento']
		del contable['Cuenta Contable']
		del contable['Debe']
		del contable['Haber']
		del contable['Número']
		del contable['Rut']
		"""

		#contable = contable.reindex(['id','Saldo','Fecha','cuenta'], axis=1)

		df = pd.pivot_table(contable,
							index = ["cuenta", "id"],
							values = ["Saldo"],
							#columns = ["Rut"],
							aggfunc = [np.sum],
							fill_value = 0,
							margins = True,
							dropna= True
							).reset_index()


		with pd.ExcelWriter('testFactura.xlsx') as writer:  
			df.to_excel(writer, sheet_name='contable')


		metadata = sqlalchemy.MetaData()
		engine = sqlalchemy.create_engine('sqlite:///testFactura.db', echo=False)
		metadata = sqlalchemy.MetaData()

		metadata.create_all(engine)
		contable.to_sql('contable', engine, if_exists='replace')



		cnx = sqlite3.connect('testFactura.db')

		consulta  = "SELECT \
						contable.* \
					FROM \
						contable \
		"

		datos = pd.read_sql_query(consulta, cnx)

		writer = pd.ExcelWriter('Comparabilidad_de_estados_financieros.xlsx', engine='xlsxwriter')
		datos.to_excel(writer, sheet_name='Todas las cuentas')
		writer.save()







if __name__ == '__main__':
	Database()


