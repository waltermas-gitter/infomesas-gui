#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("pendientes_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from pedidos WHERE estado='pendiente'")
    data = cur.fetchall()
    pedidos_fecha = []
    for item in data:
        pedidos_fecha.append((item[0], datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S"), item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12]))
    data = sorted(pedidos_fecha, key=lambda x: x[1])
 
    pedidos = []
    orden = 0
    pendientes = 0
    enproduccion = 0
    mesAnterior = 0
    for item in data:
        orden += 1
        # fecha = datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
        fechap = "%s-%s" % (item[1].day, item[1].month)
        cur.execute("SELECT nombre from clientes WHERE idCliente = %s" % (item[2]))
        cliente = cur.fetchall()[0][0]
        cur.execute("SELECT modelo from modelos WHERE idmodelo = %s" % (item[3]))
        modelo = cur.fetchall()[0][0]
        cur.execute("SELECT chapa from chapas WHERE idchapa = %s" % (item[4]))
        chapa = cur.fetchall()[0][0]
        medidas = "%s-%s*%s" % (item[6], item[7], item[8])
        pedidos.append((orden, fechap, cliente, modelo , chapa, medidas, item[5]))    

    html_template_string = template.render(pedidos=pedidos)
    # print(html_template_string)

    pedidos_file = open("pendientes.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
