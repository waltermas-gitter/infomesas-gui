#!/bin/python3

import sqlite3
from datetime import datetime, timedelta
import os
from jinja2 import Template

def main():
    jinja2_template_string = open("soldini_template.html", 'r').read()
    template = Template(jinja2_template_string)
    conn = sqlite3.connect('infomesas.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM deudas WHERE proveedor = 1")
    data_raw = cur.fetchall()
    data = []
    total = 0
    for item in data_raw:
        total += item[4]
        # print(item)
        fecha = datetime.strptime(item[2], "%Y-%m-%d %H:%M:%S")
        fechap = "%s-%s-%s" % (fecha.day, fecha.month, fecha.year)
        if item[4] >= 0:
            data.append((fechap, item[3], item[4], " ", total))
        else:
            data.append((fechap, item[3], " ", item[4], total))
    deuda_pendiente = []
    total_general = total
    data_raw.reverse() 
    for item in data_raw:
        if item[4] > 0:
            if total > 0 :
                fecha = datetime.strptime(item[2], "%Y-%m-%d %H:%M:%S")
                fechap = "%s-%s-%s" % (fecha.day, fecha.month, fecha.year)
                demora = datetime.today() - fecha
                demora_txt = "%s" % (demora.days)
                if total < item[4]:
                    deuda_pendiente.append((fechap, item[3], total, "%s dias" % demora_txt))
                else:
                    deuda_pendiente.append((fechap, item[3], item[4], "%s dias" % demora_txt))
            total -= item[4]
    deuda_pendiente.reverse()

    html_template_string = template.render(data=data, total=total_general, deuda_pendiente=deuda_pendiente)
    # print(html_template_string)

    soldini_file = open("soldini.html", 'w').write(html_template_string)

if __name__ == '__main__':
    main()

