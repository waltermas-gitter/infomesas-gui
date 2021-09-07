#!/bin/python3

import sqlite3
# from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("cada_cliente_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('../infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes ORDER BY nombre")
    # clientes = []
    clientes = cur.fetchall()
    for cliente in clientes:
        curPedidos = conn.cursor()
        curPedidos.execute("SELECT * FROM pedidos WHERE cliente = '%s'" % cliente[0])
        dataPedidos = curPedidos.fetchall()
        for pedido in dataPedidos:
            # print(pedido)
            pass
        html_template_string = template.render(cliente=cliente[1])
        clienteFileName = cliente[1].replace(' ', '-')
        clienteFileName += '.html'
        template_file = open(clienteFileName, 'w').write(html_template_string)

if __name__ == '__main__':
    main()
