#!/bin/bash
cd /home/waltermas/MEGAsync/scripts/infomesas-gui/mobile
poetry run python m_generar_pendientes_jinja.py
poetry run python m_generar_cada_cliente_jinja.py
poetry run python m_generar_todos_pedidos_jinja.py

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
notify-send "infomesas actualizado con exito"
