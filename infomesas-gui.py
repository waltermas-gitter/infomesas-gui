#!/usr/bin/env python3

# https://waltermas-gitter.github.io/infomesas-gui/
# https://realpython.com/python-pyqt-database/

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem, QDateEdit, QItemDelegate
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
# from PyQt5 import QtGui 
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

    
class ComboDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QComboBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):

        QItemDelegate.__init__(self, parent)


class InfomesasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("infomesasmain.ui", self)

        self.initUI()

    def initUI(self):
        self.actionSalir.triggered.connect(self.salir)

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

        #model
        # Set up the model
        self.model = QSqlTableModel(self)
        self.model.setTable("pedidos")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        # self.model.setHeaderData(0, Qt.Horizontal, "ID")
        # self.model.setHeaderData(1, Qt.Horizontal, "Name")
        # self.model.setHeaderData(2, Qt.Horizontal, "Job")
        # self.model.setHeaderData(3, Qt.Horizontal, "Email")
        self.model.select()
        # Set up the view
        # self.view = QTableView()

        self.pedidosTableView.setItemDelegateForColumn(1, ComboDelegate(self))
        self.pedidosTableView.setModel(self.model)
        self.pedidosTableView.resizeColumnsToContents()

        # https://stackoverflow.com/questions/45249904/how-to-use-qwidget-with-qitemdelegate-and-qtableview

    def salir(self):
        con.close()
        sys.exit(0)


    
def window():
    app = QApplication(sys.argv)
    win = InfomesasWindow()
    win.show()
    sys.exit(app.exec_())

window()

