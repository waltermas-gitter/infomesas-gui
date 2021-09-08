#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template

conn = sqlite3.connect('../infomesas.db')

def main():
    jinja2_template_string = open("cada_cliente_template.html", 'r').read()
    template = Template(jinja2_template_string)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes ORDER BY nombre")
    # clientes = []
    clientes = cur.fetchall()
    for cliente in clientes:
        curPedidos = conn.cursor()
        curPedidos.execute("SELECT * FROM pedidos WHERE cliente = '%s'" % cliente[0])
        pedidos = []
        dataPedidos = curPedidos.fetchall()
        for pedido in dataPedidos:
            # print(pedido)
            fechaPedido = datetime.strptime(pedido[1], "%Y-%m-%d %H:%M:%S")
            fechap = fechaPedido.strftime("%d-%m-%Y")
            idModelo = devuelvoNombreModelo(pedido[3])
            idChapa = devuelvoNombreChapa(pedido[4])
            
            pedidos.append((fechap, idModelo, idChapa, pedido[5], pedido[6], pedido[7], pedido[8]))
        # print(clienteFileName)
        html_template_string = template.render(cliente=cliente[1], pedidos=pedidos)
        clienteFileName = cliente[1].replace(' ', '-')
        clienteFileName += '.html'
        template_file = open(clienteFileName, 'w').write(html_template_string)

def devuelvoNombreModelo(id):
    cur = conn.cursor()
    cur.execute("SELECT modelo FROM modelos WHERE idModelo = '%s'" % id)
    data = cur.fetchall()
    return data[0][0]

def devuelvoNombreChapa(id):
    cur = conn.cursor()
    cur.execute("SELECT chapa FROM chapas WHERE idChapa = '%s'" % id)
    data = cur.fetchall()
    return data[0][0]
 
def devuelvoNombreLugarEntrega(id):
    queryLugarEntrega = QSqlQuery("SELECT nombre FROM lugaresEntrega WHERE idLugarEntrega = '%s'" % id)
    queryLugarEntrega.first()
    return(queryLugarEntrega.value(0))
 
if __name__ == '__main__':
    main()
