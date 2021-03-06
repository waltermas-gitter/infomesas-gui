#!/usr/bin/env python3 

import sqlite3
# from datetime import datetime, timedelta
import os
from jinja2 import Template, FileSystemLoader, Environment
from coloresClientes import devuelvoColorCliente
import codecs

env = Environment()
env.loader = FileSystemLoader('.')

def main():
    conn = sqlite3.connect('../infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from clientes ORDER BY nombre")
    clientes = []
    data = cur.fetchall()
    for item in data:
        ofuscado = codecs.encode(item[1].replace(' ', '-'), 'rot_13')
        clientes.append((item[1], "%s.html" % ofuscado, devuelvoColorCliente(item[1])))
        # clientes.append((item[1], "https://waltermas-gitter.github.io/infomesas-gui/mobile/%s.html" % ofuscado, devuelvoColorCliente(item[1])))

    tmpl = env.get_template('clientes_template.html')
    html_template_string = tmpl.render(clientes=clientes)
    template_file = open("clientes.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
