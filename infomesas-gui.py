#!/usr/bin/env python3

# https://realpython.com/python-pyqt-database/

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import sys

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
    

class PedidoWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("pedido.ui", self)



class InfomesasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("infomesasmain.ui", self)

        self.initUI()

    def initUI(self):
        self.actionSalir.triggered.connect(self.salir)
        self.pushButton.clicked.connect(self.editarPedido)

        self.pedidosTableWidget.setColumnCount(4)
        self.pedidosTableWidget.setHorizontalHeaderLabels(["ID", "Name", "Job", "Email"])
        query = QSqlQuery("SELECT idPedido, fecha, cliente, modelo FROM pedidos")
        while query.next():        
            rows = self.pedidosTableWidget.rowCount()
            self.pedidosTableWidget.setRowCount(rows + 1)
            self.pedidosTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            self.pedidosTableWidget.setItem(rows, 1, QTableWidgetItem(query.value(1)))
            self.pedidosTableWidget.setItem(rows, 2, QTableWidgetItem(str(query.value(2))))
            self.pedidosTableWidget.setItem(rows, 3, QTableWidgetItem(query.value(3)))
        self.pedidosTableWidget.resizeColumnsToContents()                    

    def editarPedido(self):
        self.pedido = PedidoWindow()
        print(self.pedido)
        self.pedido.show()

    def salir(self):
        con.close()
        sys.exit(0)


    
def window():
    app = QApplication(sys.argv)
    win = InfomesasWindow()
    win.show()
    
    sys.exit(app.exec_())

window()

