import xlrd
import csv

def csv_from_excel():
    wb = xlrd.open_workbook('C:/Users/Hector/Documents/desarrollo/acepta/CarteraFinancieraPresupuestaria/Cartera Financiera Presupuestaria - Devengo Cartera Financiera - 12abril202112_43_49.xlsx')
    sh = wb.sheet_by_name('Sheet1')
    your_csv_file = open('your_csv_file.csv', 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()








import pandas as pd

df = pd.read_csv('your_csv_file.csv')

print(df) 


writer = pd.ExcelWriter('contable.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Todas las cuentas')
writer.save()
# runs the csv_from_excel function:
csv_from_excel()