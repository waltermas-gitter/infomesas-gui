#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("cc_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('infomesas.db')
    cur = conn.cursor()

    cur.execute("SELECT nombre, saldo from clientes WHERE saldo != 0")
    data = cur.fetchall()
    total = 0
    for item in data:
        total += item[1]


    html_template_string = template.render(data=data, total=total)
    # print(html_template_string)

    pedidos_file = open("cc.html", 'w').write(html_template_string)



if __name__ == '__main__':
    main()


