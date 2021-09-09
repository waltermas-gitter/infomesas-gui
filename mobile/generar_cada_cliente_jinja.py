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
        curPedidos.execute("SELECT * FROM pedidos WHERE cliente = '%s' ORDER BY fecha DESC" % cliente[0])
        pedidos = []
        dataPedidos = curPedidos.fetchall()
        for pedido in dataPedidos:
            # print(pedido)
            fechaPedido = datetime.strptime(pedido[1], "%Y-%m-%d %H:%M:%S")
            fechap = fechaPedido.strftime("%d-%m-%Y")
            modelo = devuelvoNombreModelo(pedido[3])
            chapa = devuelvoNombreChapa(pedido[4])
            if pedido[11]:
                fechaEntregada = datetime.strptime(pedido[11], "%Y-%m-%d %H:%M:%S")
                fechapentregada = fechaPedido.strftime("%d-%m-%Y")
                lugarEntrega = devuelvoNombreLugarEntrega(pedido[12])
            else:
                fechapentregada = ""
                lugarEntrega = ""
            # print(pedidos)
            
            pedidos.append((fechap, modelo, chapa, pedido[5], pedido[6], pedido[7], pedido[8], pedido[9], pedido[10], fechapentregada, lugarEntrega))
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
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM lugaresEntrega WHERE idLugarEntrega = '%s'" % id)
    data = cur.fetchall()
    return data[0][0]

if __name__ == '__main__':
    main()
