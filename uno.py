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

		self.parseCarteraFinancieraPresupuestaria()

	def parseCarteraFinancieraPresupuestaria(self):

		# 11643980-8

		for f in glob.glob('CarteraFinancieraPresupuestaria/Cartera Financiera Presupuestaria*.xlsx', recursive=True):
			wb = xlrd.open_workbook(f)
			sh = wb.sheet_by_name('Sheet1')
			your_csv_file = open('your_csv_file.csv', 'w')
			wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
			for rownum in range(sh.nrows):
				wr.writerow(sh.row_values(rownum))
			your_csv_file.close()
			presupuesto = pd.read_csv('your_csv_file.csv')

			print( sorted(presupuesto) )

			presupuesto['Tipo Vista']		= presupuesto.drop( presupuesto[ presupuesto['Tipo Vista'] == 'Saldo Inicial' ].index , inplace=True )
			presupuesto['Fecha Documento']	= self.normalizeDate(presupuesto['Fecha Documento'])
			presupuesto['Fecha Documento']	= pd.to_datetime(presupuesto['Fecha Documento']).dt.date
			presupuesto['Rut']				= presupuesto['Principal'].str.split(' ', n = 1, expand = True)[0]
			presupuesto['id']				= presupuesto['Rut'] + presupuesto['Número Documento']

			del presupuesto['Principal']
			del presupuesto['Monto Documento']
			del presupuesto['Monto Documento.1']
			del presupuesto['Tipo Documento']
			del presupuesto['Folio']
			del presupuesto['Tipo Vista']
			del presupuesto['Título']
			del presupuesto['Fecha Generación']
			del presupuesto['Concepto']

			#presupuesto = presupuesto.reindex(['id', 'Fecha Documento'], axis=1)

			presupuesto.set_index('id')



			writer = pd.ExcelWriter('presupuesto.xlsx', engine='xlsxwriter')
			presupuesto.to_excel(writer, sheet_name='Todas las cuentas')
			writer.save()

			print(">>>>>>>>>>> Roger Roger")

if __name__ == '__main__':
	Database()