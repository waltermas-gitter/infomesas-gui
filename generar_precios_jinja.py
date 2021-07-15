#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("precios_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('infomesas.db')
    cur = conn.cursor()
    cur.execute("SELECT idProducto from productosSeguidosPrecios ORDER BY idProducto")
    data = cur.fetchall()
    precios = []
    dataSinDuplicados = list(dict.fromkeys(data))
    for item in dataSinDuplicados:
        cur.execute("SELECT * from productosSeguidosPrecios WHERE idProducto = '%s'" % item[0])
        dataProducto = cur.fetchall()
        # print(dataProducto)
        precioMaximo = max(dataProducto, key=lambda i: i[2])
        dataNombreProducto = cur.execute("SELECT * from productosSeguidos WHERE idProducto = '%s'" % precioMaximo[1])
        nombreProducto = cur.fetchall()
    #     print(nombreProducto[0][1])
        # print(precioMaximo[2])
    #     print()
        precios.append((nombreProducto[0][1], precioMaximo[2]))

    precios.sort()
    html_template_string = template.render(precios=precios)
    precios_file = open("precios.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()
