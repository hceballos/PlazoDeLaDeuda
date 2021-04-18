import sqlalchemy
import pandas as pd
import glob
import sqlite3
import numpy as np
from datetime import datetime
from datetime import date
import re
import xlrd







class Database():


	def normalizeDateConta(self, dateString):
		return dateString.replace(['(\d{2}).(\d{2}).(\d{2})?(\d{2})'], ['\g<4>-\g<2>-\g<1>'], regex=True)

	def normalizeDate(self, dateString):
		return dateString.replace(['(\d{2})\/(\d{2})\/(\d{4})'], ['\g<3>-\g<2>-\g<1>'], regex=True)

	def __init__(self):


		self.parseCarteraFinancieraPresupuestaria()

	def parseCarteraFinancieraPresupuestaria(self):
		presupuesto = pd.DataFrame()
		# Cartera Financiera Presupuestaria: cuentas 22, 29, 34
		for f in glob.glob('CarteraFinancieraPresupuestaria/Cartera*'):
			df = pd.read_excel(open(f, 'rb'), sheet_name='Sheet1') 	


			df = df.drop(df.index[range(10)])
			print('Procesando  : ', f)
			presupuesto = presupuesto.append(df,ignore_index=False)




		loc = ("CarteraFinancieraPresupuestaria/Cartera Financiera Presupuestaria - Devengo Cartera Financiera - 15abril202113_11_08.xlsx")
		wb = xlrd.open_workbook(loc)
		print(wb, type(wb))
		#presupuesto['Tipo Vista']	= presupuesto.drop( presupuesto[ presupuesto['Tipo Vista'] == 'Saldo Inicial' ].index , inplace=True )
		#presupuesto['Fecha Documento']		= self.normalizeDate(presupuesto['Fecha Documento'])
		#presupuesto['Fecha Documento']		= pd.to_datetime(presupuesto['Fecha Documento']).dt.date

		# 11643980-8
		"""
		del presupuesto['Principal']
		del presupuesto['Monto Documento']
		del presupuesto['Monto Documento.1']
		del presupuesto['Tipo Documento']
		del presupuesto['Folio']
		del presupuesto['Tipo Vista']
		del presupuesto['Título']
		del presupuesto['Fecha Generación']
		del presupuesto['Concepto']
		"""

		#presupuesto = presupuesto.reindex(['id','Fecha Documento', 'Rut', 'Número Documento' ], axis=1)

		metadata = sqlalchemy.MetaData()
		engine = sqlalchemy.create_engine('sqlite:///presupuesto.db', echo=False)
		metadata = sqlalchemy.MetaData()

		metadata.create_all(engine)
		presupuesto.to_sql('presupuesto', engine, if_exists='replace')
		#wb.to_sql('presupuesto', engine, if_exists='wb')


		cnx = sqlite3.connect('presupuesto.db')
		consulta  = (""" 
			SELECT 
				presupuesto.*
			FROM 
				presupuesto
		""")

		conta = pd.read_sql_query(consulta, cnx)

		with pd.ExcelWriter('presupuesto.xlsx') as writer: 
			presupuesto.to_excel(writer, sheet_name='presupuesto')
			wb.to_excel(writer, sheet_name='wb')

		print(">>>>>>>>>>> FIN")

if __name__ == '__main__':
	Database()