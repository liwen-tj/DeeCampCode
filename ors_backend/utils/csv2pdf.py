# 需要安装pdfkit、wkhtmltopdf

import pdfkit as pdf
import pandas as pd
import os
import numpy as np


def csv2pdf(csv_file):
    HTML_TEMPLATE1 = '''<html>
    <head><meta charset="gbk">
    <style>
      h2 {
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
      }
      table { 
        margin-left: auto;
        margin-right: auto;
      }
      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
      }
      th, td {
        padding: 5px;
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 90%;
      }
      table tbody tr:hover {
        background-color: #dddddd;
      }
      .wide {
        width: 90%; 
      }
    </style>
    </head>
    <body>
    <h2 align='center'>手术室排班表</h2>
    '''
    HTML_TEMPLATE2 = '''</body>
    </html>
    '''

    # csv_file = '../data/preview.csv'
    html_file = csv_file[:-3] + 'html'
    pdf_file = csv_file[:-3] + 'pdf'

    df = pd.read_csv(csv_file, sep=',', encoding='gbk')
    # print(df.head())
    df.drop(columns=['key', 'rank'], inplace=True)
    df.index = np.arange(1, len(df) + 1) # 设置从1开始
    # print(df.head())

    df.to_html(html_file, justify='center')
    formatter = ''
    with open(html_file) as fr:
        tmp = fr.read()
        formatter = HTML_TEMPLATE1 + tmp + HTML_TEMPLATE2

    with open(html_file, 'w') as fw:
        fw.write(formatter)

    pdf.from_file(html_file, pdf_file)
    os.remove(html_file)
