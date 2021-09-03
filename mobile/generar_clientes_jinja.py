#!/bin/python3

import sqlite3
# from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("clientes_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('../infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from clientes ORDER BY nombre")
    clientes = []
    data = cur.fetchall()
    for item in data:
        clientes.append(item[1])
        print(item[1])

    html_template_string = template.render(clientes=clientes)
    # print(html_template_string)

    template_file = open("clientes.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
