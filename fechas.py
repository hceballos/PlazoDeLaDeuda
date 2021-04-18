import sqlalchemy
import pandas as pd
import glob
import sqlite3
import numpy as np
from datetime import datetime
from datetime import date
import re
import xlrd
import csv

class Database():


	def normalizeDateConta(self, dateString):
		return dateString.replace(['(\d{2}).(\d{2}).(\d{2})?(\d{2})'], ['\g<4>-\g<2>-\g<1>'], regex=True)

	def normalizeDate(self, dateString):
		return dateString.replace(['(\d{2})\/(\d{2})\/(\d{4})'], ['\g<3>-\g<2>-\g<1>'], regex=True)

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
		#contable['Fecha']	= pd.to_datetime(contable['Fecha']).dt.date

		#contable['Fecha']	= self.normalizeDateConta(contable['Fecha'])
		contable['Fecha']	= pd.to_datetime(contable['Fecha']).dt.date


		contable['Rut']		= contable['Principal'].str.split(' ', n = 1, expand = True)[0]
		contable['cuenta']	= contable['Cuenta Contable'].str.split(' ', n = 1, expand = True)[0]
		contable['Saldo']	= contable['Haber'] - contable['Debe']
		contable['id']		= contable['Rut'] + contable['Número']
		#contable.index.name = 'foo'

		del contable['Principal']
		del contable['Tipo Movimiento']
		del contable['Folio']
		del contable['Título']
		del contable['Saldo Acumulado']
		del contable['Tipo Documento']
		del contable['Cuenta Contable']
		#del contable['Debe']
		#del contable['Haber']

		contable['antiguedad'] =  (max(contable['Fecha']) - contable['Fecha']).dt.days
		contable.loc[contable['antiguedad']  < 31, 'Plazo de la deuda'] = '1. Hasta 30 días' 
		contable.loc[(contable['antiguedad'] > 30) & (contable['antiguedad'] < 46), 'Plazo de la deuda'] = '2. Entre 31 y 45 días' 
		contable.loc[(contable['antiguedad'] > 45) & (contable['antiguedad'] < 61), 'Plazo de la deuda'] = '3. Entre 46 y 60 días' 
		contable.loc[(contable['antiguedad'] > 60) & (contable['antiguedad'] < 91), 'Plazo de la deuda'] = '4. Entre 61 y 90 días' 
		contable.loc[(contable['antiguedad'] > 90) & (contable['antiguedad'] < 121), 'Plazo de la deuda'] = '5. Entre 91 y 120 días' 
		contable.loc[(contable['antiguedad'] > 120) & (contable['antiguedad'] < 151), 'Plazo de la deuda'] = '6. Entre 121 y 150 días' 
		contable.loc[contable['antiguedad']  > 150, 'Plazo de la deuda'] = '7. Más de 150 días' 

		contable = contable.reindex(['id','Saldo', 'Fecha', 'Debe','Haber', 'Rut', 'Número', 'cuenta', 'antiguedad', 'Plazo de la deuda'], axis=1)

		self.parseCarteraFinancieraPresupuestaria(contable)

	def parseCarteraFinancieraPresupuestaria(self, contable):
		for f in glob.glob('CarteraFinancieraPresupuestaria/Cartera Financiera Presupuestaria*.xlsx', recursive=True):
			wb = xlrd.open_workbook(f)
			sh = wb.sheet_by_name('Sheet1')
			your_csv_file = open('your_csv_file.csv', 'w')
			wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
			for rownum in range(sh.nrows):
				wr.writerow(sh.row_values(rownum))
			your_csv_file.close()
			presupuesto = pd.read_csv('your_csv_file.csv')


			presupuesto['Tipo Vista']		= presupuesto.drop( presupuesto[ presupuesto['Tipo Vista'] == 'Saldo Inicial' ].index , inplace=True )
			presupuesto['Fecha Documento']	= self.normalizeDate(presupuesto['Fecha Documento'])
			presupuesto['Fecha Documento']	= pd.to_datetime(presupuesto['Fecha Documento']).dt.date
			presupuesto['Rut']				= presupuesto['Principal'].str.split(' ', n = 1, expand = True)[0]
			presupuesto['id']				= presupuesto['Rut'] + presupuesto['Número Documento']
			presupuesto.set_index('id')



			del presupuesto['Principal']
			del presupuesto['Monto Documento']
			del presupuesto['Monto Documento.1']
			del presupuesto['Tipo Documento']
			del presupuesto['Folio']
			del presupuesto['Tipo Vista']
			del presupuesto['Título']
			del presupuesto['Fecha Generación']
			del presupuesto['Concepto']

			presupuesto = presupuesto.reindex(['id', 'Fecha Documento', 'Rut', 'Número Documento'], axis=1)
			self.parseServicioDeLaDeuda(contable, presupuesto)

	def parseServicioDeLaDeuda(self, contable, presupuesto):
		servicioDeLaDeuda = pd.DataFrame()
		for f in glob.glob('CarteraFinancieraPresupuestaria/servicioDeLaDeuda.xlsx', recursive=True):
			df = pd.read_excel(f, converters={ 'Número Documento': str }, engine='openpyxl' )
			df = df.drop(df.index[range(10)])
			print('Procesando  : ', f)
			servicioDeLaDeuda = servicioDeLaDeuda.append(df,ignore_index=True)

		servicioDeLaDeuda['Tipo Vista']				= servicioDeLaDeuda.drop( servicioDeLaDeuda[ servicioDeLaDeuda['Tipo Vista'] == 'Saldo Inicial' ].index , inplace=True )
		servicioDeLaDeuda['Fecha Generación']		= pd.to_datetime(servicioDeLaDeuda['Fecha Generación']).dt.date
		servicioDeLaDeuda['Fecha Documento']		= pd.to_datetime(servicioDeLaDeuda['Fecha Documento']).dt.date
		servicioDeLaDeuda['Rut']					= servicioDeLaDeuda['Principal'].str.split(' ', n = 1, expand = True)[0]
		servicioDeLaDeuda['id']						= servicioDeLaDeuda['Rut'] + servicioDeLaDeuda['Número Documento']

		del servicioDeLaDeuda['Principal']
		del servicioDeLaDeuda['Monto Documento']
		del servicioDeLaDeuda['Monto Documento.1']
		del servicioDeLaDeuda['Tipo Documento']
		del servicioDeLaDeuda['Folio']
		del servicioDeLaDeuda['Tipo Vista']
		del servicioDeLaDeuda['Título']
		del servicioDeLaDeuda['Fecha Documento']
		del servicioDeLaDeuda['Concepto']
		#del servicioDeLaDeuda['Número Documento']
		#del servicioDeLaDeuda['Rut']
		
		servicioDeLaDeuda = servicioDeLaDeuda.reindex(['id', 'Fecha Generación', 'Rut', 'Número Documento'], axis=1)

		metadata = sqlalchemy.MetaData()
		engine = sqlalchemy.create_engine('sqlite:///plazoDeLaDeuda1.db', echo=False)
		metadata = sqlalchemy.MetaData()

		metadata.create_all(engine)
		contable.to_sql('contable', engine, if_exists='replace')
		presupuesto.to_sql('presupuesto', engine, if_exists='replace')
		servicioDeLaDeuda.to_sql('servicioDeLaDeuda', engine, if_exists='replace')


		cnx = sqlite3.connect('plazoDeLaDeuda1.db')
		cursor = cnx.cursor()
		cursor.execute("""		
		CREATE TABLE IF NOT EXISTS conta AS
			SELECT 
				contable.id as id, 
				contable.cuenta as cuenta, 
				contable.Fecha as Fecha, 
				contable.antiguedad as antiguedad, 
				contable.Rut as rut,
				contable.Número as numero,
				contable.'Plazo de la deuda' as 'Plazo de la deuda', 
				sum(contable.Saldo) as saldo 
			FROM 
				contable 
			GROUP BY  
				contable.id 
			HAVING  
				sum(contable.Saldo) <> 0 
			ORDER BY 
				cuenta asc 
		""")



		consulta  = (""" 
			SELECT 
				conta.*
			FROM 
				conta
		""")

		conta = pd.read_sql_query(consulta, cnx)


		frames = [conta, presupuesto]
		result2 = pd.concat([conta, presupuesto.reindex(conta.index)], axis=1)
		result4 = pd.merge(conta, presupuesto, on="id")
		result5 = pd.merge(presupuesto, conta, how="right", on=["id", "id"])
		result51 = result5.groupby(by=["Plazo de la deuda"]).sum()

		result6 = pd.merge(conta, presupuesto, how="inner", on=["id", "id"])
		result61 = result6.groupby(by=["Plazo de la deuda"]).sum()

		result7 = pd.merge(presupuesto, conta, how="left",  on=["id", "id"])
		result71 = result7.groupby(by=["Plazo de la deuda"]).sum()

		with pd.ExcelWriter('plazoDeLaDeuda1.xlsx') as writer: 
			conta.to_excel(writer, sheet_name='conta')
			presupuesto.to_excel(writer, sheet_name='presupuesto')
			result2.to_excel(writer, sheet_name='result2')
			result4.to_excel(writer, sheet_name='result4')
			result5.to_excel(writer, sheet_name='result5')
			result6.to_excel(writer, sheet_name='result6')
			result7.to_excel(writer, sheet_name='result7')
			result71.to_excel(writer, sheet_name='result71')
			result61.to_excel(writer, sheet_name='result61')
			result51.to_excel(writer, sheet_name='result51')





		print(">>>>>>>>>>> FIN")

if __name__ == '__main__':
	Database()