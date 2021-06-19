#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("pedidos_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT * from pedidos")
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
        demoratxt = ' '
        if item[10] == 'pendiente':
            estado = "<td style='color:green'>pendiente</td>"
            pendientes += 1
            demora = datetime.today() - item[1]
            demoratxt = demora.days
        elif item[10] == 'en produccion':
            enproduccion += 1
            estado = "<td style='color:brown'>en produccion</td>"
        elif item[10] == 'terminada':
            estado = "<td>terminada</td>"
        else:
            estado = "<td>%s</td>" % item[10]
        if item[11] == None:
            fecha_entregada_p = ''
        else:
            fecha_entregada = datetime.strptime(item[11], "%Y-%m-%d %H:%M:%S")
            fecha_entregada_p = "%s-%s" % (fecha_entregada.day, fecha_entregada.month)
        if item[12] == None:
            lugarEntrega = ''
        else:
            cur.execute("SELECT nombre from lugaresEntrega WHERE idLugarEntrega = %s" % (item[12]))
            lugarEntrega = cur.fetchall()[0][0]
        # clavesPedidos[orden] = item[0] 
        if mesAnterior != item[1].month:
            pedidos.append('  ')
            pedidos.append(("<span style='color:blue'>%s</span>" % item[1].year, "<span style='color:blue'>%s</span>" % item[1].month))
            mesAnterior = item[1].month
     
        pedidos.append((orden, fechap, demoratxt, cliente, modelo , chapa, item[5], medidas, item[9], estado,fecha_entregada_p,lugarEntrega))    

    pedidos.append(("pendientes:", "<span style='color:green'>%s</span>" % pendientes))
    pedidos.append(("en produccion:", "<span style='color:brown'>%s</span>" % enproduccion))

    html_template_string = template.render(pedidos=pedidos)
    # print(html_template_string)

    pedidos_file = open("pedidos.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
