#!/usr/bin/env python3

# https://realpython.com/python-pyqt-database/

# from PyQt5 import QtWidgets, uic
# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
# from PyQt5.QtSql import QSqlDatabase, QSqlQuery

# import sys
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from PyQt5 import uic
from datetime import datetime, timedelta


# Create the connection
con = QSqlDatabase.addDatabase("QSQLITE")
con.setDatabaseName("infomesas.db")

# Try to open the connection and handle possible errors
if not con.open():
    QMessageBox.critical(
        None,
        "App Name - Error!",
        "Database Error: %s" % con.lastError().databaseText(),
    )
    sys.exit(1)
    

class PedidoDialog(QDialog):
    def __init__(self, id):
        super().__init__()
        uic.loadUi("pedidoDialog.ui", self)
        self.id = id
        print(self.id)



class InfomesasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("infomesasmain.ui", self)

        self.initUI()

    def initUI(self):
        self.actionSalir.triggered.connect(self.salir)
        self.pushButton.clicked.connect(self.editarPedido)

        # lleno pedidosTableWidget
        self.pedidosTableWidget.setColumnCount(13)
        self.pedidosTableWidget.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Modelo", "Chapa", "Notas", "M.cerrada", "M.abierta", "M.ancho", "Precio", "Estado", "F.entrega", "Lugar entrega"])
        query = QSqlQuery("SELECT * FROM pedidos")
        while query.next():        
            rows = self.pedidosTableWidget.rowCount()
            self.pedidosTableWidget.setRowCount(rows + 1)
            self.pedidosTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            fecha = datetime.strptime(query.value(1), "%Y-%m-%d %H:%M:%S")
            # fechap = "%s-%s-%s" % (fecha.day, fecha.month, fecha.year)
            fechap = fecha.strftime("%d-%m-%Y")
            
            self.pedidosTableWidget.setItem(rows, 1, QTableWidgetItem(fechap))
            # cur.execute("SELECT nombre from clientes WHERE idCliente = %s" % (item[2])) 
            # cliente = cur.fetchall()[0][0] 
            queryCliente = QSqlQuery("SELECT nombre FROM clientes WHERE idCliente = %s" % query.value(2))
            queryCliente.first()
 
            self.pedidosTableWidget.setItem(rows, 2, QTableWidgetItem(str(queryCliente.value(0))))



            self.pedidosTableWidget.setItem(rows, 3, QTableWidgetItem(query.value(3)))
            self.pedidosTableWidget.setItem(rows, 4, QTableWidgetItem(str(query.value(4))))
            self.pedidosTableWidget.setItem(rows, 5, QTableWidgetItem(str(query.value(5))))
            self.pedidosTableWidget.setItem(rows, 6, QTableWidgetItem(str(query.value(6))))
            self.pedidosTableWidget.setItem(rows, 7, QTableWidgetItem(str(query.value(7))))
            self.pedidosTableWidget.setItem(rows, 8, QTableWidgetItem(str(query.value(8))))
            self.pedidosTableWidget.setItem(rows, 9, QTableWidgetItem(str(query.value(9))))
            self.pedidosTableWidget.setItem(rows, 10, QTableWidgetItem(str(query.value(10))))
            self.pedidosTableWidget.setItem(rows, 11, QTableWidgetItem(str(query.value(11))))
            self.pedidosTableWidget.setItem(rows, 12, QTableWidgetItem(str(query.value(12))))

        self.pedidosTableWidget.resizeColumnsToContents()                    

    def editarPedido(self):
        item = self.pedidosTableWidget.item(self.pedidosTableWidget.currentRow(),0)
        self.pedido = PedidoDialog(item.text())
        if self.pedido.exec_() == QDialog.Accepted:
            print("aceptado")


    def salir(self):
        con.close()
        sys.exit(0)


    
def window():
    app = QApplication(sys.argv)
    win = InfomesasWindow()
    win.show()
    
    sys.exit(app.exec_())

window()

