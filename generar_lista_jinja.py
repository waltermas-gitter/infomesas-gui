#!/bin/python3

import sqlite3
# from datetime import datetime, timedelta
import os
from jinja2 import Template



def main():
    jinja2_template_string = open("lista_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from precios2 WHERE modelo='nro 100'")
    data = cur.fetchall()
    nro100 = []
    for item in data:
        nro100.append((item[2], item[3], item[4]))
    html_template_string = template.render(nro100=nro100)
# print(html_template_string)

    modelos_file = open("lista.html", 'w').write(html_template_string)
    


if __name__ == '__main__':
    main()
