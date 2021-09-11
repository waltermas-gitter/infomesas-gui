#!/bin/python3

import sqlite3
# from datetime import datetime, timedelta
import os
from jinja2 import Template
from coloresClientes import devuelvoColorCliente
import codecs

def main():
    jinja2_template_string = open("clientes_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('../infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from clientes ORDER BY nombre")
    clientes = []
    data = cur.fetchall()
    for item in data:
        ofuscado = codecs.encode(item[1].replace(' ', '-'), 'rot_13')
        clientes.append((item[1], "https://waltermas-gitter.github.io/infomesas-gui/mobile/%s.html" % ofuscado, devuelvoColorCliente(item[1])))
        # os.system("rm %s.html" % item[1].replace(' ', '-'))

    html_template_string = template.render(clientes=clientes)
    template_file = open("clientes.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
