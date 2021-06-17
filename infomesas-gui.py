#!/usr/bin/env python3

# https://realpython.com/python-pyqt-database/
# lista de precios en pedidos
# filtro en productos seguidos
# web
# push
# recordar vista al empezar



import os, sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from PyQt5 import uic
from datetime import datetime, timedelta
import calendar
import iconosResource_rc # pyrcc5 iconosResource.qrc -o iconosResource_rc.py
import re
# https://www.mfitzp.com/tutorials/qresource-system/



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
        self.clientesPushButton.clicked.connect(self.showClientes)
        self.productosSeguidosPushButton.clicked.connect(self.showProductosSeguidos)
        self.chequesPushButton.clicked.connect(self.showCheques)
        self.salirPushButton.clicked.connect(self.close)
        self.pushPushButton.clicked.connect(self.pushear)

        # lleno pedidosTableWidget
        # self.visualizarQuery("SELECT * FROM pedidos")
        self.vistaChanged()


    def visualizarQuery(self, queryString):
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
            self.vistaChanged()


    def showProveedores(self):
        self.prov = ProveedoresWindow()
        self.prov.show()

    def showClientes(self):
        self.cliente = ClientesWindow()
        self.cliente.show()

    def showProductosSeguidos(self):
        self.productosSeguidos = ProductosSeguidosWindow()
        self.productosSeguidos.show()

    def showCheques(self):
        self.cheques = ChequesWindow()
        self.cheques.show()



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

    def pushear(self):
        stdouterr = os.popen("./actualizar.sh")[1].read()
        # os.system("./actualizar.sh")
        print(stdouterr)





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
        self.okPushButton.clicked.connect(self.save)
        self.cancelPushButton.clicked.connect(self.reject)
        self.filterListaLineEdit.textChanged.connect(self.mostrarLista)
        self.ultimaLista=open('ultimalista.txt').readlines()
        # self.mostrarLista()


    def cambioEstado(self):
        if self.estadoListWidget.currentItem().text() == 'entregada':
            self.fechaEntregaDateEdit.setEnabled(True)
            self.lugarEntregaComboBox.setEnabled(True)
        else:
            self.fechaEntregaDateEdit.setEnabled(False)
            self.lugarEntregaComboBox.setEnabled(False)
 

    def save(self):
        # checks
        if self.modeloListWidget.currentRow() == -1:
            mensaje("modelo no seleccionado")
            return
        if self.chapaListWidget.currentRow() == -1:
            mensaje("chapa no seleccionada")
            return
        if self.clienteComboBox.currentText() == " [elegir]":
            mensaje("cliente no seleccionado")
            return




        #save
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
        self.accept()
    
    def mostrarLista(self):
        filtradoLista = []
        for item in self.ultimaLista:
            if self.filterListaLineEdit.text() in item:
                filtradoLista.append(item)
        filtradoString = ''.join(filtradoLista)
        self.listaPlainTextEdit.setPlainText(filtradoString)
        
            


class SumasSaldosDialog(QDialog):
    def __init__(self, id, esProveedor):  #esProveedor=True proveedor, sino es cliente
        super().__init__()
        uic.loadUi("sumasSaldos.ui", self)
        self.id = id
        self.esProveedor = esProveedor
        # self.returnValues = []
        self.initUI()

    def initUI(self):
        if self.esProveedor == True:
            self.setWindowTitle(devuelvoNombreProveedor(self.id))
        else:
            self.setWindowTitle(devuelvoNombreCliente(self.id))
        self.nuevoPushButton.clicked.connect(self.nuevoMovimiento)
        self.salirPushButton.clicked.connect(self.accept)
        self.sumasSaldosTableWidget.setColumnCount(6)
        self.sumasSaldosTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.sumasSaldosTableWidget.setHorizontalHeaderLabels(["Id", "Fecha", "Concepto", "Debe", "Haber", "Saldo"])
        self.sumasSaldosTableWidget.itemDoubleClicked.connect(self.movimiento)
        self.cargarTabla()
        

    def cargarTabla(self):
        self.sumasSaldosTableWidget.setRowCount(0)
        if self.esProveedor == True:
            queryString = "SELECT * FROM deudas WHERE proveedor = '%s'" % self.id
        else:
            queryString = "SELECT * FROM cuentasCorrientes WHERE cliente = '%s'" % self.id
        query = QSqlQuery(queryString)
        saldo = 0
        while query.next():        
            rows = self.sumasSaldosTableWidget.rowCount()
            self.sumasSaldosTableWidget.setRowCount(rows + 1)
            self.sumasSaldosTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            fecha = datetime.strptime(query.value(2), "%Y-%m-%d %H:%M:%S")
            fechap = fecha.strftime("%d-%m-%Y")
            self.sumasSaldosTableWidget.setItem(rows, 1, QTableWidgetItem(fechap))
            self.sumasSaldosTableWidget.setItem(rows, 2, QTableWidgetItem(query.value(3)))
            sumaItem = QTableWidgetItem(str(query.value(4)))
            sumaItem.setTextAlignment(Qt.AlignRight)
            if query.value(4) >= 0:
                self.sumasSaldosTableWidget.setItem(rows, 3, sumaItem)
            else:
                sumaItem.setText(sumaItem.text()[1:]) # le saco el signo negativo
                self.sumasSaldosTableWidget.setItem(rows, 4, sumaItem)
            saldo += query.value(4)
            saldoItem = QTableWidgetItem(str(saldo))
            saldoItem.setTextAlignment(Qt.AlignRight)
            self.sumasSaldosTableWidget.setItem(rows, 5, saldoItem)

        self.sumasSaldosTableWidget.scrollToBottom()
        self.sumasSaldosTableWidget.resizeColumnsToContents()



    def movimiento(self):
        # idMovimiento = self.sumasSaldosTableWidget.selectedItems()[0].text()
        self.mov = Movimiento(self.sumasSaldosTableWidget.selectedItems(), self.id, self.esProveedor)
        if self.mov.exec_() == QDialog.Accepted:
            print("aceptado")
            self.cargarTabla()
            # row = int(self.pedidosTableWidget.selectedItems()[0].text())
            # for i in range(len(self.mov.returnValues)):
                # self.sumasSaldosTableWidget.selectedItems()[i].setText(self.mov.returnValues[i])

        # self.show()

    def nuevoMovimiento(self):
        self.mov = Movimiento(0, self.id, self.esProveedor)
        if self.mov.exec_() == QDialog.Accepted:
            self.cargarTabla()
 






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
        self.cargarTabla()

    def sumasSaldosShow(self):
        self.sumasSaldos = SumasSaldosDialog(self.proveedoresTableWidget.selectedItems()[0].text(), True)
        if self.sumasSaldos.exec_() == QDialog.Accepted:
            self.cargarTabla()

    def cargarTabla(self):
        self.proveedoresTableWidget.setRowCount(0)
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






class ClientesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("clientes.ui", self)
        self.initUI()

    def initUI(self):
        self.clientesTableWidget.setColumnCount(3)
        self.clientesTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.clientesTableWidget.setHorizontalHeaderLabels(["ID", "Cliente", "Saldo"])
        self.clientesTableWidget.itemDoubleClicked.connect(self.sumasSaldosShow)
        self.cargarTabla()

    def sumasSaldosShow(self):
        self.sumasSaldos = SumasSaldosDialog(self.clientesTableWidget.selectedItems()[0].text(), False)
        if self.sumasSaldos.exec_() == QDialog.Accepted:
            self.cargarTabla()

    def cargarTabla(self):
        self.clientesTableWidget.setRowCount(0)
        query = QSqlQuery("SELECT * FROM clientes")
        while query.next():        
            rows = self.clientesTableWidget.rowCount()
            self.clientesTableWidget.setRowCount(rows + 1)
            self.clientesTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            self.clientesTableWidget.setItem(rows, 1, QTableWidgetItem(devuelvoNombreCliente(query.value(0))))
            saldo = QTableWidgetItem(str(query.value(5)))
            saldo.setTextAlignment(Qt.AlignRight)
            self.clientesTableWidget.setItem(rows, 2, QTableWidgetItem(saldo))
        self.clientesTableWidget.resizeColumnsToContents()







class Movimiento(QDialog):
    def __init__(self, id, provId, esProveedor):
        super().__init__()
        uic.loadUi("movimiento.ui", self)
        self.id = id
        self.provId = provId
        self.esProveedor = esProveedor
        self.initUI()

    def initUI(self):
        # lleno los items correspondientes
        # id = 0 implica nuevo pedido
        if self.id == 0:
            self.fechaDateEdit.setDate(QDate.currentDate())
            self.importeLineEdit.setText('0')
        else:
            dialist = self.id[1].text().split('-')
            dia = QDate(int(dialist[2]), int(dialist[1]), int(dialist[0]))
            self.fechaDateEdit.setDate(dia)
            self.conceptoLineEdit.setText(self.id[2].text())

            # for i in range(5):
                # print(self.id[i].text())
            if self.esProveedor == True:
                queryString = "SELECT importe FROM deudas WHERE idDeuda = '%i'" % int(self.id[0].text())
            else:
                queryString = "SELECT importe FROM cuentasCorrientes WHERE idcc = '%i'" % int(self.id[0].text())
            querySigno = QSqlQuery(queryString)
            querySigno.first()
            
            if querySigno.value(0) >= 0:
                self.debeRadioButton.setChecked(True)
            else:
                self.haberRadioButton.setChecked(True)
            importe = int(self.id[3].text())
            self.importeLineEdit.setText(str(importe))

        # self.dialogButtonBox.accepted.connect(self.save)
        self.okPushButton.clicked.connect(self.save)
        self.cancelPushButton.clicked.connect(self.reject)


    def save(self):
        query = QSqlQuery()
        
        if self.id == 0:
            if self.esProveedor == True:
                queryString = "INSERT INTO deudas (proveedor, fecha, concepto, importe) VALUES (:proveedor, :fecha, :concepto, :importe)"
            else:
                queryString = "INSERT INTO cuentasCorrientes (cliente, fecha, concepto, importe) VALUES (:proveedor, :fecha, :concepto, :importe)"
            query.prepare(queryString)
        
        else:
            if self.esProveedor == True:
                queryString = "UPDATE deudas SET proveedor=:proveedor, fecha=:fecha, concepto=:concepto, importe=:importe WHERE idDeuda = :idDeuda"
            else:
                queryString = "UPDATE cuentasCorrientes SET cliente=:proveedor, fecha=:fecha, concepto=:concepto, importe=:importe WHERE idcc = :idDeuda"
            query.prepare(queryString)
            query.bindValue(":idDeuda", int(self.id[0].text()))

        query.bindValue(":proveedor", self.provId)
        dia = self.fechaDateEdit.date().toPyDate()
        diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
        query.bindValue(":fecha", diaString)
        query.bindValue(":concepto", self.conceptoLineEdit.text())
        importe = int(self.importeLineEdit.text())
        if self.haberRadioButton.isChecked() == True:
          importe = importe * (-1) 
        query.bindValue(":importe", importe)
        query.exec_()

        if self.esProveedor == True:
            # actualizo saldo en tabla proveedores
            queryImportes = QSqlQuery("SELECT importe FROM deudas WHERE Proveedor = '%s'" % self.provId)
            saldo = 0
            while queryImportes.next():
                saldo += queryImportes.value(0)
            queryProveedor = QSqlQuery("UPDATE proveedores SET saldo = '%s' WHERE idProveedor = '%s'" % (saldo, self.provId))
        else:
            # actualizo saldo en tabla clientes
            queryImportes = QSqlQuery("SELECT importe FROM cuentasCorrientes WHERE cliente = '%s'" % self.provId)
            saldo = 0
            while queryImportes.next():
                saldo += queryImportes.value(0)
            queryProveedor = QSqlQuery("UPDATE clientes SET saldo = '%s' WHERE idCliente = '%s'" % (saldo, self.provId))
        self.accept()


 



class ProductosSeguidosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("productosSeguidos.ui", self)
        self.initUI()

    def initUI(self):
        self.nuevoPushButton.clicked.connect(self.nuevoProducto)
        self.productosSeguidosTableWidget.setColumnCount(5)
        self.productosSeguidosTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.productosSeguidosTableWidget.setHorizontalHeaderLabels(["ID", "Descripcion", "Fecha", "Proveedor", "Precio"])
        self.productosSeguidosTableWidget.itemDoubleClicked.connect(self.historialPreciosShow)
        self.cargarTabla()

    def historialPreciosShow(self):
        self.historialPrecios = HistorialPreciosDialog(self.productosSeguidosTableWidget.selectedItems())
        if self.historialPrecios.exec_() == QDialog.Accepted:
            self.cargarTabla()

    def cargarTabla(self):
        self.productosSeguidosTableWidget.setRowCount(0)
        query = QSqlQuery("SELECT * FROM productosSeguidos")
        while query.next():        
            rows = self.productosSeguidosTableWidget.rowCount()
            self.productosSeguidosTableWidget.setRowCount(rows + 1)
            self.productosSeguidosTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            self.productosSeguidosTableWidget.setItem(rows, 1, QTableWidgetItem(query.value(1)))
            queryPrecio = QSqlQuery("SELECT * FROM productosSeguidosPrecios WHERE idProducto = '%s'" % query.value(0))
            queryPrecio.last()
            if queryPrecio.value(1):
                fecha = datetime.strptime(queryPrecio.value(4), "%Y-%m-%d %H:%M:%S")
                fechap = fecha.strftime("%d-%m-%Y")
                self.productosSeguidosTableWidget.setItem(rows, 2, QTableWidgetItem(fechap))
                prov = devuelvoNombreProveedor(queryPrecio.value(3))
                self.productosSeguidosTableWidget.setItem(rows, 3, QTableWidgetItem(prov))
                precioItem = QTableWidgetItem(str(queryPrecio.value(2)))
                precioItem.setTextAlignment(Qt.AlignRight)
                self.productosSeguidosTableWidget.setItem(rows, 4, precioItem)
        
        self.productosSeguidosTableWidget.resizeColumnsToContents()
        
    def nuevoProducto(self):
        descripcion, okPressed = QInputDialog.getText(self, "Nuevo producto","Descripcion", QLineEdit.Normal, "")
        if okPressed and descripcion != '':
            query = QSqlQuery("INSERT INTO productosSeguidos (descripcion) VALUES ('%s')" % descripcion) 
            self.cargarTabla()


        


class HistorialPreciosDialog(QDialog):
    def __init__(self, id):
        super().__init__()
        uic.loadUi("historialPrecios.ui", self)
        self.id = id
        self.initUI()

    def initUI(self):
        # self.dialogButtonBox.accepted.connect(self.save)
        self.setWindowTitle(self.id[1].text())
        self.historialPreciosTableWidget.setColumnCount(4)
        self.historialPreciosTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.historialPreciosTableWidget.setHorizontalHeaderLabels(["ID", "Proveedor", "Fecha", "Precio"])
        # self.historialPreciosTableWidget.itemDoubleClicked.connect(self.nuevoPrecioShow)
        self.nuevoPushButton.clicked.connect(self.nuevoPrecioShow)
        # self.dialogButtonBox.accepted.connect(self.accept)
        self.okPushButton.clicked.connect(self.accept)

       # lleno los items correspondientes
        
        # productos = []
        # productos.append('[nuevo]')
        # while queryProductos.next():
        #     productos.append(queryProductos.value(1))
        # self.productosSeguidosComboBox.addItems(productos)

        # if self.id == 0:
        #     self.fechaDateEdit.setDate(QDate.currentDate())
        #     self.importeLineEdit.setText('0')
        # else:
            
            # self.fechaDateEdit.setDate(dia)
            # self.proveedoresComboBox.setCurrentText(self.id[3].text())
            # self.importeLineEdit.setText(self.id[4].text())
            # self.descripcionLineEdit.setText(self.id[1].text())
            # self.productosSeguidosComboBox.setCurrentText(self.id[1].text())

        self.cargarTabla()


    def cargarTabla(self):
        self.historialPreciosTableWidget.setRowCount(0)
        query = QSqlQuery("SELECT * FROM productosSeguidosPrecios WHERE idProducto = '%s'" % self.id[0].text())
        while query.next():        
            rows = self.historialPreciosTableWidget.rowCount()
            self.historialPreciosTableWidget.setRowCount(rows + 1)
            self.historialPreciosTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            self.historialPreciosTableWidget.setItem(rows, 1, QTableWidgetItem(devuelvoNombreProveedor(query.value(3))))
            fecha = datetime.strptime(query.value(4), "%Y-%m-%d %H:%M:%S")
            fechap = fecha.strftime("%d-%m-%Y")
            self.historialPreciosTableWidget.setItem(rows, 2, QTableWidgetItem(fechap))
            self.historialPreciosTableWidget.setItem(rows, 3, QTableWidgetItem(str(query.value(2))))

    def nuevoPrecioShow(self):
        # self.nuevoPrecio = NuevoPrecioDialog(self.historialPreciosTableWidget.selectedItems())
        self.nuevoPrecio = NuevoPrecioDialog(self.id)
        if self.nuevoPrecio.exec_() == QDialog.Accepted:
            self.cargarTabla()


    #     if self.id == 0:
    #         if self.productosSeguidosComboBox.currentText() == '[nuevo]':
    #             query = QSqlQuery("INSERT INTO productosSeguidos (descripcion) VALUES ('%s')" % self.descripcionLineEdit.text())
    #         # print(query.lastInsertId())
    #             productoId = query.lastInsertId()
    #         else:
    #             productoId = self.id[0].text()

    #         queryPS = QSqlQuery() 
    #         queryPS.prepare("INSERT INTO productosSeguidosPrecios (idProducto, precio, proveedor, fecha) VALUES (:idProducto, :precio, :proveedor, :fecha)")
    #         queryPS.bindValue(":idProducto", productoId)
    #         queryPS.bindValue(":precio", self.importeLineEdit.text())
    #         queryPS.bindValue(":proveedor", devuelvoIdProveedor(self.proveedoresComboBox.currentText()))
    #         dia = self.fechaDateEdit.date().toPyDate()
    #         diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
    #         queryPS.bindValue(":fecha", diaString)
    #         queryPS.exec_()

    #     else:
    #         query = QSqlQuery("UPDATE productosSeguidos SET descripcion = '%s' WHERE idProducto = '%s'" % (self.descripcionLineEdit.text(), self.id[0].text()))
            
    #         dia = datetime.strptime(self.id[2].text(),"%d-%m-%Y")
    #         diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
    #         query = QSqlQuery("SELECT idProductoPrecio FROM productosSeguidosPrecios WHERE idProducto = '%s' AND proveedor = '%s' AND fecha = '%s'" % (self.id[0].text(), devuelvoIdProveedor(self.id[3].text()), diaString))
    #         query.first()
    #         queryPS = QSqlQuery()
    #         queryPS.prepare("UPDATE productosSeguidosPrecios SET precio=:precio, proveedor=:proveedor, fecha=:fecha WHERE idProductoPrecio=:idProductoPrecio")
    #         queryPS.bindValue(":precio", self.importeLineEdit.text())
    #         queryPS.bindValue(":proveedor", devuelvoIdProveedor(self.proveedoresComboBox.currentText()))
    #         dia = self.fechaDateEdit.date().toPyDate()
    #         diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
    #         queryPS.bindValue(":fecha", diaString)
    #         queryPS.bindValue(":idProductoPrecio", query.value(0))
    #         queryPS.exec_()


class NuevoPrecioDialog(QDialog):
    def __init__(self, id):
        super().__init__()
        uic.loadUi("historialPreciosMov.ui", self)
        self.id = id
        self.initUI()

    def initUI(self):
        self.fechaDateEdit.setDate(QDate.currentDate())
        self.importeLineEdit.setText('0')
        proveedores = llenoProveedores()
        self.setWindowTitle(self.id[1].text())
        self.proveedoresComboBox.addItems(proveedores)
        # self.dialogButtonBox.accepted.connect(self.save)
        self.okPushButton.clicked.connect(self.save)
        self.cancelPushButton.clicked.connect(self.reject)


    def save(self):
        query = QSqlQuery() 
        query.prepare("INSERT INTO productosSeguidosPrecios (idProducto, precio, proveedor, fecha) VALUES (:idProducto, :precio, :proveedor, :fecha)")
        query.bindValue(":idProducto", self.id[0].text())
        query.bindValue(":precio", self.importeLineEdit.text())
        query.bindValue(":proveedor", devuelvoIdProveedor(self.proveedoresComboBox.currentText()))
        dia = self.fechaDateEdit.date().toPyDate()
        diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
        query.bindValue(":fecha", diaString)
        query.exec_()
        self.accept()

class ChequesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("cheques.ui", self)
        self.initUI()

    def initUI(self):
        self.chequesTableWidget.setColumnCount(9)
        self.chequesTableWidget.setSelectionBehavior(QTableView.SelectRows)
        self.chequesTableWidget.setHorizontalHeaderLabels(["ID", "Recibido", "Cliente", "Fecha", "Banco", "Numero", "Importe", "Entregado", "Proveedor"])
        self.chequesTableWidget.itemDoubleClicked.connect(self.editarCheque)
        self.nuevoPushButton.clicked.connect(self.nuevoCheque)
        self.cargarTabla()

    def cargarTabla(self):
        saldo = 0
        self.chequesTableWidget.setRowCount(0)
        query = QSqlQuery("SELECT * FROM cheques")
        while query.next():        
            rows = self.chequesTableWidget.rowCount()
            self.chequesTableWidget.setRowCount(rows + 1)
            self.chequesTableWidget.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            fecha = datetime.strptime(query.value(1), "%Y-%m-%d %H:%M:%S")
            fechap = fecha.strftime("%d-%m-%Y")
            self.chequesTableWidget.setItem(rows, 1, QTableWidgetItem(fechap))
            self.chequesTableWidget.setItem(rows, 2, QTableWidgetItem(devuelvoNombreCliente(query.value(2))))
            fecha = datetime.strptime(query.value(3), "%Y-%m-%d %H:%M:%S")
            fechap = fecha.strftime("%d-%m-%Y")
            self.chequesTableWidget.setItem(rows, 3, QTableWidgetItem(fechap))
            self.chequesTableWidget.setItem(rows, 4, QTableWidgetItem(query.value(4)))
            self.chequesTableWidget.setItem(rows, 5, QTableWidgetItem(str(query.value(5))))
            importe = QTableWidgetItem(str(query.value(6)))
            importe.setTextAlignment(Qt.AlignRight)
            self.chequesTableWidget.setItem(rows, 6, QTableWidgetItem(importe))
            if query.value(7):
                fecha = datetime.strptime(query.value(7), "%Y-%m-%d %H:%M:%S")
                fechap = fecha.strftime("%d-%m-%Y")
                proveedorWidget = QTableWidgetItem(devuelvoNombreProveedor(query.value(8)))
            else:
                fechap = None
                proveedorWidget = QTableWidgetItem('disponible')
                proveedorWidget.setForeground(QBrush(QColor('green')))
                saldo += query.value(6)

            self.chequesTableWidget.setItem(rows, 7, QTableWidgetItem(fechap))
            self.chequesTableWidget.setItem(rows, 8, proveedorWidget)
            
 

        self.chequesTableWidget.resizeColumnsToContents()
        self.statusbar.showMessage("Total disponible: %s" % saldo)


    def editarCheque(self):
        self.cheque = ChequeDialog(self.chequesTableWidget.selectedItems())
        if self.cheque.exec_() == QDialog.Accepted:
            self.cargarTabla()

    def nuevoCheque(self):
        self.cheque = ChequeDialog(0)
        if self.cheque.exec_() == QDialog.Accepted:
            self.cargarTabla()






class ChequeDialog(QDialog):
    def __init__(self, id):
        super().__init__()
        uic.loadUi("chequeDialog.ui", self)
        self.id = id
        self.initUI()

    def initUI(self):
        self.proveedorComboBox.currentTextChanged.connect(self.chequeEntregado)
        # self.dialogButtonBox.accepted.connect(self.save)
        self.okPushButton.clicked.connect(self.save)
        self.cancelPushButton.clicked.connect(self.reject)
        clientes = llenoClientes()
        self.clienteComboBox.addItems(clientes)
 
        proveedores = llenoProveedores()
        self.proveedorComboBox.addItems(proveedores)

        if self.id == 0:
            self.recibidoDateEdit.setDate(QDate.currentDate())
            self.fechaChequeDateEdit.setDate(QDate.currentDate())
            self.fechaEntregadoDateEdit.setDate(QDate.currentDate())
            self.fechaEntregadoDateEdit.setEnabled(False)
            self.proveedorComboBox.setCurrentText("[elegir]")

        else:
            dialist = self.id[1].text().split('-')
            dia = QDate(int(dialist[2]), int(dialist[1]), int(dialist[0]))
            self.recibidoDateEdit.setDate(dia)
            self.clienteComboBox.setCurrentText(self.id[2].text())
            dialist = self.id[3].text().split('-')
            dia = QDate(int(dialist[2]), int(dialist[1]), int(dialist[0]))
            self.fechaChequeDateEdit.setDate(dia)
            self.bancoLineEdit.setText(self.id[4].text())
            self.numeroLineEdit.setText(self.id[5].text())
            self.importeLineEdit.setText(self.id[6].text())
            if self.id[7].text() != '':
                dialist = self.id[7].text().split('-')
                dia = QDate(int(dialist[2]), int(dialist[1]), int(dialist[0]))
                self.fechaEntregadoDateEdit.setDate(dia)
                self.proveedorComboBox.setCurrentText(self.id[8].text())
            else:
                self.fechaEntregadoDateEdit.setDate(QDate.currentDate())
                self.fechaEntregadoDateEdit.setEnabled(False)
                self.proveedorComboBox.setCurrentText("[elegir]")

    def chequeEntregado(self):
        if self.proveedorComboBox.currentText() != "[elegir]":
            self.fechaEntregadoDateEdit.setEnabled(True)

    def save(self):
        # check
        if self.clienteComboBox.currentText() == " [elegir]":
            mensaje("cliente no seleccionado")
            return
        if self.bancoLineEdit.text() == '':
            mensaje("banco no seleccionado")
            return
        if self.numeroLineEdit.text() == '':
            mensaje("numero no seleccionado")
            return
        if self.importeLineEdit.text() == '':
            mensaje("importe no seleccionado")
            return



        #save
        query = QSqlQuery()
        if self.id == 0:
            query.prepare("INSERT INTO cheques (fechaRecibido, cliente, fechaCheque, banco, numero, importe, fechaEntregado, entregadoA) VALUES (:fechaRecibido, :cliente, :fechaCheque, :banco, :numero, :importe, :fechaEntregado, :entregadoA)")
        else:
            query.prepare("UPDATE cheques SET fechaRecibido=:fechaRecibido, cliente=:cliente, fechaCheque=:fechaCheque, banco=:banco, importe=:importe, fechaEntregado=:fechaEntregado, entregadoA=:entregadoA WHERE idCheque=:idCheque")
            query.bindValue(":idCheque", int(self.id[0].text()))
        dia = self.recibidoDateEdit.date().toPyDate()
        diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
        query.bindValue(":fechaRecibido", diaString)
        query.bindValue(":cliente", devuelvoIdCliente(self.clienteComboBox.currentText()))
        dia = self.fechaChequeDateEdit.date().toPyDate()
        diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
        query.bindValue(":fechaCheque", diaString)
        query.bindValue(":banco", self.bancoLineEdit.text())
        query.bindValue(":numero", self.numeroLineEdit.text())
        query.bindValue(":importe", int(self.importeLineEdit.text()))
        if self.fechaEntregadoDateEdit.isEnabled() == True:
            dia = self.fechaEntregadoDateEdit.date().toPyDate()
            diaString = datetime.strftime(dia, "%Y-%m-%d %H:%M:%S")
            query.bindValue(":fechaEntregado", diaString)
            query.bindValue(":entregadoA", devuelvoIdProveedor(self.proveedorComboBox.currentText()))
        query.exec_()
        self.accept()



 
        
            


 
def llenoClientes():
    clientes = []
    clientes.append(" [elegir]")
    query = QSqlQuery("SELECT nombre FROM clientes")
    while query.next():
        clientes.append(query.value(0))
    clientes.sort()
    return(clientes)

def llenoProveedores():
    proveedores = []
    # proveedores.append(" [elegir]")
    query = QSqlQuery("SELECT nombre FROM proveedores")
    while query.next():
        proveedores.append(query.value(0))
    proveedores.sort()
    return(proveedores)


def devuelvoIdCliente(nombre):
    queryCliente = QSqlQuery("SELECT idCliente FROM clientes WHERE nombre = '%s'" % nombre)
    queryCliente.first()
    return(queryCliente.value(0))

def devuelvoNombreCliente(id):
    queryCliente = QSqlQuery("SELECT nombre FROM clientes WHERE idCliente = '%s'" % id)
    queryCliente.first()
    return(queryCliente.value(0))

def devuelvoIdProveedor(nombre):
    queryProveedor = QSqlQuery("SELECT idProveedor FROM proveedores WHERE nombre = '%s'" % nombre)
    queryProveedor.first()
    return(queryProveedor.value(0))

def devuelvoNombreProveedor(id):
    queryProveedor = QSqlQuery("SELECT nombre FROM proveedores WHERE idProveedor = '%s'" % id)
    queryProveedor.first()
    return(queryProveedor.value(0))

def mensaje(texto):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(texto)
    msgBox.setWindowTitle("Error")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    

    
def window():
    app = QApplication(sys.argv)
    win = InfomesasWindow()
    win.show()
    
    sys.exit(app.exec_())

window()

