#!/usr/bin/env python3 

import os
from jinja2 import Template, FileSystemLoader, Environment

env = Environment()
env.loader = FileSystemLoader('.')

def main():
    targets = []
    targets.append({"carpeta":"../fotos/recta", "htmlfile":"fotos_recta.html"})
    targets.append({"carpeta":"../fotos/nro100", "htmlfile":"fotos_nro100.html"})
    targets.append({"carpeta":"../fotos/cubo", "htmlfile":"fotos_cubo.html"})
    targets.append({"carpeta":"../fotos/escandinava", "htmlfile":"fotos_escandinava.html"})
    targets.append({"carpeta":"../fotos/especiales", "htmlfile":"fotos_especiales.html"})
    targets.append({"carpeta":"../fotos/ratonas-auxiliares", "htmlfile":"fotos_ratonas-auxiliares.html"})
    targets.append({"carpeta":"../fotos/redonda", "htmlfile":"fotos_redonda.html"})

    for item in targets:
        mypath = item["carpeta"]
        fotos = [mypath[2:] + "/" + f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]    
        fotoactiva = fotos[0]
        fotos.pop(0)
        tmpl = env.get_template('fotos_template.html')
        html_template_string = tmpl.render(fotoactiva=fotoactiva, fotos=fotos)
        template_file = open(item["htmlfile"], 'w').write(html_template_string)

if __name__ == '__main__':
    main()
