import sqlalchemy
import pandas as pd
import glob
import sqlite3
import numpy as np
from datetime import datetime
from datetime import date

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

		contable = contable.reindex(['id','Saldo','Fecha','cuenta'], axis=1)

		self.parseCarteraFinancieraPresupuestaria(contable)

	def parseCarteraFinancieraPresupuestaria(self, 
		contable):
		presupuesto = pd.DataFrame()
		# Cartera Financiera Presupuestaria: cuentas 22, 29, 34
		for f in glob.glob('CarteraFinancieraPresupuestaria/Cartera*', recursive=True):
			df = pd.read_excel(f, converters={ 'Número Documento': str }, engine='openpyxl' )
			df = df.drop(df.index[range(10)])
			print('Procesando  : ', f)
			presupuesto = presupuesto.append(df,ignore_index=True)

		presupuesto['Tipo Vista']	= presupuesto.drop( presupuesto[ presupuesto['Tipo Vista'] == 'Saldo Inicial' ].index , inplace=True )
		presupuesto['Fecha Generación']		= pd.to_datetime(presupuesto['Fecha Generación']).dt.date

		#presupuesto['Fecha Documento']		= pd.to_datetime(presupuesto['Fecha Documento']).dt.date
		presupuesto['Fecha Documento']		= pd.to_datetime(presupuesto['Fecha Documento']).dt.date
		presupuesto['Rut']					= presupuesto['Principal'].str.split(' ', n = 1, expand = True)[0]
		presupuesto['id']					= presupuesto['Rut'] + presupuesto['Número Documento']

		del presupuesto['Principal']
		del presupuesto['Monto Documento']
		del presupuesto['Monto Documento.1']
		del presupuesto['Tipo Documento']
		del presupuesto['Folio']
		del presupuesto['Tipo Vista']
		del presupuesto['Título']
		del presupuesto['Fecha Generación']
		del presupuesto['Concepto']
		del presupuesto['Número Documento']
		del presupuesto['Rut']


		presupuesto = presupuesto.reindex(['id','Fecha Documento'], axis=1)

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
		del servicioDeLaDeuda['Número Documento']
		del servicioDeLaDeuda['Rut']
		
		servicioDeLaDeuda = servicioDeLaDeuda.reindex(['id', 'Fecha Generación'], axis=1)

		with pd.ExcelWriter('plazoDeLaDeuda1.xlsx') as writer:  
			contable.to_excel(writer, sheet_name='contable')
			presupuesto.to_excel(writer, sheet_name='presupuesto')
			servicioDeLaDeuda.to_excel(writer, sheet_name='servicioDeLaDeuda')

		"""
		metadata = sqlalchemy.MetaData()
		engine = sqlalchemy.create_engine('sqlite:///database.db', echo=False)
		metadata = sqlalchemy.MetaData()

		metadata.create_all(engine)
		contable.to_sql('contable', engine, if_exists='replace')
		presupuesto.to_sql('presupuesto', engine, if_exists='replace')
		servicioDeLaDeuda.to_sql('servicioDeLaDeuda', engine, if_exists='replace')
		"""
		print(">>>>>>>>>>> FIN")