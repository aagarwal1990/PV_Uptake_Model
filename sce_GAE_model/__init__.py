from datetime import datetime

import xlrd
import xlwt

from sce_generate_yaml_dct import GenerateYamlFromExcel
import sce_simulation_init

book = xlrd.open_workbook("ExcelMockup_v6.xlsm")

yaml_specs = GenerateYamlFromExcel(book)
                 
model = sce_simulation_init.specparser()

model.main(yaml_specs)

    
"""

style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
    num_format_str='#,##0.00')
style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

wb = xlwt.Workbook()
ws = wb.add_sheet('A Test Sheet')

ws.write(0, 0, 1234.56, style0)
ws.write(1, 0, datetime.now(), style1)
ws.write(2, 0, 1)
ws.write(2, 1, 1)
ws.write(2, 2, xlwt.Formula("A3+B3"))

wb.save('example.xls') 
"""   