#!/bin/bash
TIMEFORMAT='%3U'
cd /home/waltermas/MEGAsync/scripts/infomesas-gui/mobile
echo -n "generar pendientes mobile "
time poetry run python m_generar_pendientes_jinja.py 
echo -n "generar cada cliente mobile "
time poetry run python m_generar_cada_cliente_jinja.py
# echo -n "generar todos los pedidos mobile "
# time poetry run python m_generar_todos_pedidos_jinja.py

cd /home/waltermas/MEGAsync/scripts/infomesas-gui
poetry run python generar_cheques_jinja.py
# poetry run python generar_pedidos_jinja.py
# poetry run python generar_precios_jinja.py
poetry run python generar_soldini_jinja.py
poetry run python generar_deudas_jinja.py
# poetry run python generar_cc_jinja.py
# poetry run python generar_pendientes_jinja.py

git status
git add -A
git status
message=`date`
git commit -m "$message"
git push
# notify-send "infomesas actualizado con exito"
read -n1 -s -r -p $'Press any key to continue...\n' key
