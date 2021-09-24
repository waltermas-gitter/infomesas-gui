#!/usr/bin/env python3 
# https://www.w3schools.com/colors/colors_names.asp

def devuelvoColorCliente(cliente):
    if cliente == "Ernesto":
        color = 'green'
    elif cliente == "Raul":
        color = 'brown'
    elif cliente == "Maria Rosa":
        color = 'magenta'
    elif cliente == "Barzante":
        color = 'goldenrod'
    elif cliente == "Dalzotto":
        color = 'blue'
    elif cliente == "Guffanti":
        color = 'red'
    else:
        color = 'DarkSlateGrey'
    return color
