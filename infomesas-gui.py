#!/usr/bin/env python3

# https://realpython.com/python-pyqt-database/

# from PyQt5 import QtWidgets, uic
# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
# from PyQt5.QtSql import QSqlDatabase, QSqlQuery

# import sys

# select cliente from pedidos where fecha BETWEEN "2021-01-01" and "2021-02-02"

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from PyQt5 import uic
from datetime import datetime, timedelta
import calendar

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
        self.returnValues = []
        self.initUI()

    def initUI(self):
        clientes = llenoClientes()
        self.clienteComboBox.addItems(clientes)
        query = QSqlQuery("SELECT modelo FROM modelos")
        while query.next():
            self.modeloListWidget.addItem(query.value(0))
        query = QSqlQuery("SELECT chapa FROM chapas")
        while query.next():
            self.chapaListWidget.addItem(query.value(0))
        estados = ['pendiente', 'en produccion', 'terminada', 'entregada', 'anulada']
        self.estadoListWidget.addItems(estados)
        query = QSqlQuery("SELECT nombre FROM lugaresEntrega")
        while query.next():
            self.lugarEntregaComboBox.addItem(query.value(0))


        # lleno los items correspondientes
        # id = 0 implica nuevo pedido
        if self.id == 0:
            print('pedido nuevo')
            self.fechaDateEdit.setDate(QDate.currentDate())
            self.precioLineEdit.setText('0')
            estadoItem = self.estadoListWidget.findItems('pendiente', Qt.MatchExactly)
            self.estadoListWidget.setCurrentItem(estadoItem[0])

        else:
            dialist = self.id[1].text().split('-')
            dia = QDate(int(dialist[2]), int(dialist[1]), int(dialist[0]))
            self.fechaDateEdit.setDate(dia)
            self.clienteComboBox.setCurrentText(self.id[2].text())
            modeloItem = self.modeloListWidget.findItems(self.id[3].text(), Qt.MatchExactly)
            self.modeloListWidget.setCurrentItem(modeloItem[0])
            chapaItem = self.chapaListWidget.findItems(self.id[4].text(), Qt.MatchExactly)
            self.chapaListWidget.setCurrentItem(chapaItem[0])
            self.notasPlainTextEdit.setPlainText(self.id[5].text())
            self.medidaCerradaSpinBox.setValue(int(self.id[6].text()))
            self.medidaAbiertaSpinBox.setValue(int(self.id[7].text()))
            self.anchoSpinBox.setValue(int(self.id[8].text()))
            self.precioLineEdit.setText(self.id[9].text())
            estadoItem = self.estadoListWidget.findItems(self.id[10].text(), Qt.MatchExactly)
            self.estadoListWidget.setCurrentItem(estadoItem[0])
            if self.id[11].text() != '':
                dialist = self.id[11].text().split('-')
                dia = QDate(int(dialist[2]), int(dialist[1]), int(dialist[0]))
                self.fechaEntregaDateEdit.setDate(dia)
                self.lugarEntregaComboBox.setCurrentText(self.id[12].text())

            else:
                self.fechaEntregaDateEdit.setDate(QDate.currentDate())
                self.fechaEntregaDateEdit.setEnabled(False)
                self.lugarEntregaComboBox.setEnabled(False)

            # self.lugarEntregaComboBox.setCurrentText(self.id[12].text())

        self.estadoListWidget.itemSelectionChanged.connect(self.cambioEstado)
        self.dialogButtonBox.accepted.connect(self.save)

    def cambioEstado(self):
        if self.estadoListWidget.currentItem().text() == 'entregada':
            self.fechaEntregaDateEdit.setEnabled(True)
            self.lugarEntregaComboBox.setEnabled(True)
        else:
            self.fechaEntregaDateEdit.setEnabled(False)
            self.lugarEntregaComboBox.setEnabled(False)
 


    def save(self):
        query = QSqlQuery()
        if self.id == 0:
            query.prepare("INSERT INTO pedidos (fecha, cliente, modelo, chapa, notas, medidaCerrada, medidaAbierta, medidaAncho, precio, estado, fechaEntrega, lugarEntrega) VALUES (:fecha, :cliente, :modelo, :chapa, :notas, :medidaCerrada, :medidaAbierta, :medidaAncho, :precio, :estado, :fechaEntrega, :lugarEntrega)")
            self.returnValues.append(0)
        else:
            query.prepare("UPDATE pedidos SET fecha=:fecha, cliente=:cliente, modelo=:modelo, chapa=:chapa, notas=:notas, medidaCerrada=:medidaCerrada, medidaAbierta=:medidaAbierta, medidaAncho=:medidaAncho, precio=:precio, estado=:estado, fechaEntrega=:fechaEntrega, lugarEntrega=:lugarEntrega WHERE idPedido = :idPedido")
            query.bindValue(":idPedido", int(self.id[0].text()))
            self.returnValues.append(self.id[0].text())

        dia = self.fechaDateEdit.date().toPyDate()
        diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
        query.bindValue(":fecha", diaString)
        # queryCliente = QSqlQuery("SELECT idCliente FROM clientes WHERE nombre = '%s'" % self.clienteComboBox.currentText())
        # queryCliente.first()
        # query.bindValue(":cliente", queryCliente.value(0))
        query.bindValue(":cliente", devuelvoIdCliente(self.clienteComboBox.currentText()))
        modelo = self.modeloListWidget.currentItem().text()
        queryModelo = QSqlQuery("SELECT idModelo FROM modelos WHERE modelo = '%s'" % modelo)
        queryModelo.first()
        query.bindValue(":modelo", queryModelo.value(0))
        chapa = self.chapaListWidget.currentItem().text()
        queryChapa = QSqlQuery("SELECT idChapa FROM chapas WHERE chapa = '%s'" % chapa)
        queryChapa.first()
        query.bindValue(":chapa", queryChapa.value(0))
        query.bindValue(":notas", self.notasPlainTextEdit.toPlainText())
        query.bindValue(":medidaCerrada", self.medidaCerradaSpinBox.value())
        query.bindValue(":medidaAbierta", self.medidaAbiertaSpinBox.value())
        query.bindValue(":medidaAncho", self.anchoSpinBox.value())
        query.bindValue(":precio", int(self.precioLineEdit.text()))
        query.bindValue(":estado", self.estadoListWidget.currentItem().text())
        if self.fechaEntregaDateEdit.isEnabled() == True:
            dia = self.fechaEntregaDateEdit.date().toPyDate()
            diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
            query.bindValue(":fechaEntrega", diaString)
            queryEntrega = QSqlQuery("SELECT idLugarEntrega FROM lugaresEntrega WHERE nombre = '%s'" % self.lugarEntregaComboBox.currentText())
            queryEntrega.first()
            query.bindValue(":lugarEntrega", queryEntrega.value(0))
        query.exec_()

        # self.returnValues.append(self.id[0].text())
        dia = self.fechaDateEdit.date().toPyDate()
        diaString = datetime.strftime(dia, "%d-%m-%Y")
        self.returnValues.append(diaString)
        self.returnValues.append(self.clienteComboBox.currentText())
        self.returnValues.append(self.modeloListWidget.currentItem().text())
        self.returnValues.append(self.chapaListWidget.currentItem().text())
        self.returnValues.append(self.notasPlainTextEdit.toPlainText())
        self.returnValues.append(str(self.medidaCerradaSpinBox.value()))
        self.returnValues.append(str(self.medidaAbiertaSpinBox.value()))
        self.returnValues.append(str(self.anchoSpinBox.value()))
        self.returnValues.append(self.precioLineEdit.text())
        self.returnValues.append(self.estadoListWidget.currentItem().text())
        if self.fechaEntregaDateEdit.isEnabled() == True:
            dia = self.fechaEntregaDateEdit.date().toPyDate()
            diaString = datetime.strftime(dia, "%d-%m-%Y")
            self.returnValues.append(diaString)
            self.returnValues.append(self.lugarEntregaComboBox.currentText())


class SumasSaldosDialog(QDialog):
    def __init__(self, id):
        super().__init__()
        uic.loadUi("sumasSaldos.ui", self)
        self.id = id
        # self.returnValues = []
        self.initUI()

    def initUI(self):
        self.sumasSaldosTableWidget.setColumnCount(5)
        self.sumasSaldosTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.sumasSaldosTableWidget.setHorizontalHeaderLabels(["Fecha", "Concepto", "Debe", "Haber", "Saldo"])
        # self.proveedoresTableWidget.itemDoubleClicked.connect(self.sumasSaldosShow)
        query = QSqlQuery("SELECT * FROM deudas WHERE proveedor = '%s'" % self.id)
        saldo = 0
        while query.next():        
            rows = self.sumasSaldosTableWidget.rowCount()
            self.sumasSaldosTableWidget.setRowCount(rows + 1)
            fecha = datetime.strptime(query.value(2), "%Y-%m-%d %H:%M:%S")
            fechap = fecha.strftime("%d-%m-%Y")
            self.sumasSaldosTableWidget.setItem(rows, 0, QTableWidgetItem(fechap))
            self.sumasSaldosTableWidget.setItem(rows, 1, QTableWidgetItem(query.value(3)))
            sumaItem = QTableWidgetItem(str(query.value(4)))
            sumaItem.setTextAlignment(Qt.AlignRight)
            if query.value(4) >= 0:
                self.sumasSaldosTableWidget.setItem(rows, 2, sumaItem)
            else:
                self.sumasSaldosTableWidget.setItem(rows, 3, sumaItem)
            saldo += query.value(4)
            saldoItem = QTableWidgetItem(str(saldo))
            saldoItem.setTextAlignment(Qt.AlignRight)
            self.sumasSaldosTableWidget.setItem(rows, 4, saldoItem)

        self.sumasSaldosTableWidget.scrollToBottom()
        self.sumasSaldosTableWidget.resizeColumnsToContents()


class ProveedoresWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("proveedores.ui", self)

        self.initUI()

    def initUI(self):
        self.proveedoresTableWidget.setColumnCount(3)
        self.proveedoresTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.proveedoresTableWidget.setHorizontalHeaderLabels(["ID", "Proveedor", "Saldo"])
        self.proveedoresTableWidget.itemDoubleClicked.connect(self.sumasSaldosShow)
        query = QSqlQuery("SELECT * FROM proveedores")
        while query.next():        
            rows = self.proveedoresTableWidget.rowCount()
            self.proveedoresTableWidget.setRowCount(rows + 1)
            self.proveedoresTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            self.proveedoresTableWidget.setItem(rows, 1, QTableWidgetItem(devuelvoNombreProveedor(query.value(0))))
            saldo = QTableWidgetItem(str(query.value(5)))
            saldo.setTextAlignment(Qt.AlignRight)
            self.proveedoresTableWidget.setItem(rows, 2, QTableWidgetItem(saldo))

        self.proveedoresTableWidget.resizeColumnsToContents()


    def sumasSaldosShow(self):
        self.sumasSaldos = SumasSaldosDialog(self.proveedoresTableWidget.selectedItems()[0].text())
        self.sumasSaldos.show()




class InfomesasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("infomesasmain.ui", self)

        self.initUI()

    def initUI(self):
        self.actionSalir.triggered.connect(self.close)
        self.nuevoPushButton.clicked.connect(self.nuevoPedido)
        self.pendientesCheckBox.stateChanged.connect(self.vistaChanged)
        self.enproduccionCheckBox.stateChanged.connect(self.vistaChanged)
        self.terminadasCheckBox.stateChanged.connect(self.vistaChanged)
        self.entregadasCheckBox.stateChanged.connect(self.vistaChanged)
        self.anuladasCheckBox.stateChanged.connect(self.vistaChanged)

        self.pedidosTableWidget.setColumnCount(13)
        self.pedidosTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.pedidosTableWidget.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Modelo", "Chapa", "Notas", "cerrada", "abierta", "ancho", "Precio", "Estado", "F.entrega", "L.entrega"])
        self.pedidosTableWidget.itemDoubleClicked.connect(self.editarPedido)
        self.hastaDateEdit.setDate(QDate.currentDate())
        self.desdeDateEdit.dateChanged.connect(self.vistaChanged)
        self.hastaDateEdit.dateChanged.connect(self.vistaChanged)
        clientes = llenoClientes()
        self.clienteComboBox.addItems(clientes)
        self.clienteComboBox.currentTextChanged.connect(self.vistaChanged)
        self.proveedoresPushButton.clicked.connect(self.showProveedores)



        # lleno pedidosTableWidget
        # self.visualizarQuery("SELECT * FROM pedidos")
        self.vistaChanged()


    def visualizarQuery(self,queryString):
        self.pedidosTableWidget.setRowCount(0)
        query = QSqlQuery(queryString)
        while query.next():        
            rows = self.pedidosTableWidget.rowCount()
            self.pedidosTableWidget.setRowCount(rows + 1)
            self.pedidosTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            fecha = datetime.strptime(query.value(1), "%Y-%m-%d %H:%M:%S")
            # fechap = "%s-%s-%s" % (fecha.day, fecha.month, fecha.year)
            fechap = fecha.strftime("%d-%m-%Y")
            self.pedidosTableWidget.setItem(rows, 1, QTableWidgetItem(fechap))
            queryCliente = QSqlQuery("SELECT nombre FROM clientes WHERE idCliente = %s" % query.value(2))
            queryCliente.first()
 
            self.pedidosTableWidget.setItem(rows, 2, QTableWidgetItem(str(queryCliente.value(0))))
            queryModelo = QSqlQuery("SELECT modelo FROM modelos WHERE idModelo = '%s'" % query.value(3))
            queryModelo.first()
            self.pedidosTableWidget.setItem(rows, 3, QTableWidgetItem(queryModelo.value(0)))

            queryChapa =  QSqlQuery("SELECT chapa FROM chapas WHERE idChapa = '%s'" % query.value(4))
            queryChapa.first()
            self.pedidosTableWidget.setItem(rows, 4, QTableWidgetItem(str(queryChapa.value(0))))


            self.pedidosTableWidget.setItem(rows, 5, QTableWidgetItem(str(query.value(5))))
            medidaCerrada = QTableWidgetItem(str(query.value(6)))
            medidaCerrada.setTextAlignment(Qt.AlignRight)
            self.pedidosTableWidget.setItem(rows, 6, medidaCerrada)
            medidaAbierta = QTableWidgetItem(str(query.value(7)))
            medidaAbierta.setTextAlignment(Qt.AlignRight)
            self.pedidosTableWidget.setItem(rows, 7, medidaAbierta)
            medidaAncho = QTableWidgetItem(str(query.value(8)))
            medidaAncho.setTextAlignment(Qt.AlignRight)
            self.pedidosTableWidget.setItem(rows, 8, medidaAncho)
            precio = QTableWidgetItem(str(query.value(9)))
            precio.setTextAlignment(Qt.AlignRight)
            self.pedidosTableWidget.setItem(rows, 9, precio)
            estado = QTableWidgetItem(str(query.value(10)))
            if query.value(10) == 'pendiente':
                # estado.setForeground(QBrush(QColor(0, 255, 0)))
                estado.setForeground(QBrush(QColor('green')))
            elif query.value(10) == 'en produccion':                
                estado.setForeground(QBrush(QColor('brown')))
            elif query.value(10) == 'terminada':                
                estado.setForeground(QBrush(QColor(200,160,50)))
            self.pedidosTableWidget.setItem(rows, 10, estado)
            if query.value(11):
                fecha = datetime.strptime(query.value(11), "%Y-%m-%d %H:%M:%S")
                fechap = fecha.strftime("%d-%m-%Y")
            else:
                fechap = None
            self.pedidosTableWidget.setItem(rows, 11, QTableWidgetItem(fechap))
            if query.value(12):
                queryLugar =  QSqlQuery("SELECT nombre FROM lugaresEntrega WHERE idLugarEntrega = %s"% query.value(12))
                queryLugar.first()
                lugarEntrega = queryLugar.value(0)
            else:
                lugarEntrega = ''
            self.pedidosTableWidget.setItem(rows, 12, QTableWidgetItem(lugarEntrega))

        self.pedidosTableWidget.resizeColumnsToContents()
        # self.pedidosTableWidget.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.pedidosTableWidget.setColumnWidth(5, 150)
        self.pedidosTableWidget.scrollToBottom()
        self.statusbar.showMessage("%i registros" % self.pedidosTableWidget.rowCount())




    def editarPedido(self):
        self.pedido = PedidoDialog(self.pedidosTableWidget.selectedItems())
        if self.pedido.exec_() == QDialog.Accepted:
            print("aceptado")
            # row = int(self.pedidosTableWidget.selectedItems()[0].text())
            for i in range(len(self.pedido.returnValues)):
                self.pedidosTableWidget.selectedItems()[i].setText(self.pedido.returnValues[i])

    def nuevoPedido(self):
        self.pedido = PedidoDialog(0)
        if self.pedido.exec_() == QDialog.Accepted:
            print("aceptado")

    def showProveedores(self):
        self.prov = ProveedoresWindow()
        self.prov.show()

    def closeEvent(self, event):
        con.close()
        event.accept()
        
    # def salir(self):
    #     con.close()
    #     sys.exit(0)

    def vistaChanged(self):
        queryString = ''
        if self.pendientesCheckBox.isChecked():
            queryString = queryString + " OR estado='pendiente'"
        if self.enproduccionCheckBox.isChecked():
            queryString = queryString + " OR estado='en produccion'"
        if self.terminadasCheckBox.isChecked():
            queryString = queryString + " OR estado='terminada'"
        if self.entregadasCheckBox.isChecked():
            queryString = queryString + " OR estado='entregada'"
        if self.anuladasCheckBox.isChecked():
            queryString = queryString + " OR estado='anulada'"
        # queryString = "SELECT * FROM pedidos WHERE" + queryString
        # queryString = queryString[:28] + queryString[31:]
        queryString = queryString[3:]

        diaDesde = self.desdeDateEdit.date().toPyDate()
        diaDesdeString = datetime.strftime(diaDesde, "%Y-%m-01")
        diaHasta = self.hastaDateEdit.date().toPyDate()
        diaHastaString = datetime.strftime(diaHasta, "%Y-%m-")
        ultimoDiaMes = calendar.monthrange(int(datetime.strftime(diaHasta,"%y")), int(datetime.strftime(diaHasta,"%m")))[1]
        diaHastaString = diaHastaString + str(ultimoDiaMes)
        queryStringFecha = "SELECT * FROM pedidos WHERE (fecha BETWEEN '" + diaDesdeString + "'AND '" + diaHastaString + "') AND ("
        
        queryString = queryStringFecha + queryString + ")"
        if self.clienteComboBox.currentText() != " [elegir]":
            queryString = queryString + " AND cliente=" + str(devuelvoIdCliente(self.clienteComboBox.currentText()))

        # print(queryString)


        self.visualizarQuery(queryString)

 
def llenoClientes():
    clientes = []
    clientes.append(" [elegir]")
    query = QSqlQuery("SELECT nombre FROM clientes")
    while query.next():
        clientes.append(query.value(0))
    clientes.sort()
    return(clientes)

def devuelvoIdCliente(nombre):
    queryCliente = QSqlQuery("SELECT idCliente FROM clientes WHERE nombre = '%s'" % nombre)
    queryCliente.first()
    return(queryCliente.value(0))

def devuelvoNombreProveedor(id):
    queryProveedor = QSqlQuery("SELECT nombre FROM proveedores WHERE idProveedor = '%s'" % id)
    queryProveedor.first()
    return(queryProveedor.value(0))


    
def window():
    app = QApplication(sys.argv)
    win = InfomesasWindow()
    win.show()
    
    sys.exit(app.exec_())

window()

