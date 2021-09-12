#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template
from devuelvos import *
import codecs
from coloresClientes import devuelvoColorCliente

def main():
    jinja2_template_string = open("pendientes_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('../infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from pedidos ORDER BY fecha DESC")
    data = cur.fetchall()
    # pedidos_fecha = []
    # for item in data:
        # pedidos_fecha.append((item[0], datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S"), item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12]))
    # data = sorted(pedidos_fecha, key=lambda x: x[1])
 
    pedidos = []
    for item in data:
        fecha= datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
        fechap = "%s-%s-%s" % (fecha.day, fecha.month, fecha.year)
        nombreCliente = devuelvoNombreCliente(item[2])
        ofuscado = codecs.encode(nombreCliente.replace(' ', '-'), 'rot_13')
        linkOfuscado = "https://waltermas-gitter.github.io/infomesas-gui/mobile/%s.html" % ofuscado
        cliente = ((nombreCliente, linkOfuscado, devuelvoColorCliente(nombreCliente)))
        modelo = devuelvoNombreModelo(item[3])
        chapa = devuelvoNombreChapa(item[4])
        medidas = "%s-%s*%s" % (item[6], item[7], item[8])
        if item[11]:
            fechaEntregada = datetime.strptime(item[11], "%Y-%m-%d %H:%M:%S")
            fechapentregada = fechaEntregada.strftime("%d-%m-%Y")
            lugarEntrega = devuelvoNombreLugarEntrega(item[12])
        else:
            fechapentregada = ""
            lugarEntrega = ""
        pedidos.append((fechap, cliente, modelo , chapa, medidas, item[5], item[9], item[10], fechapentregada, lugarEntrega))    

    html_template_string = template.render(pedidos=pedidos)
    # print(html_template_string)

    pedidos_file = open("todos_pedidos.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
