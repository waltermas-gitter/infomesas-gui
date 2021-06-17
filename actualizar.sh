#!/bin/bash
cd /home/waltermas/MEGAsync/scripts/infomesas-gui
git status
git add -A
git status
message=`date`
git commit -m "$message"
git push
notify-send("infomesas actualizado con exito"
