from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
import requests
import lycanthropy.ui.connectors
import sys
import json

class FormDefault():
    def __init__(self,subTab):
        self.formGroupBox = QTabWidget(subTab)
        #self.formGroupBox.setStyleSheet("QGroupBox{background-color: rgb(245, 245, 245);border: 1px solid rgb(223, 223, 224);font: JetBrains MonoNL;}QGroupBox::title{font: JetBrains MonoNL;top: 12px;left: 10px;}")
        self.formGroupBox.move(20, 380)
        self.formGroupBox.resize(1330, 250)

class InterfaceDefault():
    def __init__(self,subTab):
        return

class AlertDefault(QDialog):
    #time to implement wolfmon eventing on server activity
    # - httpStreamProvisioner should be changed to portalStreamProvisioner and contain data for agent-focused alerting
    # - dnsStreamProvisioner should be changed to daemonStreamProvisioner and contain data related to errors on the daemon
    def __init__(self,alertData):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setWindowTitle("Lycanthropy - Wolfmon Alert")
        #self.pixmapprim = QPixmap('../Lycanthropy_logo.png')
        #self.pixmap = self.pixmapprim.scaledToHeight(200)
        #self.label = QLabel(self)
        #self.label.setPixmap(self.pixmap)

        #self.label.resize(self.pixmap.width(),
        #                  self.pixmap.height())
        #self.setStyleSheet("background-color: rgb(245, 245, 245);font-size: large;")
        #self.resize(500, 200)
        #self.calculateCorner()
        #self.alertLabel = QLabel(self)
        #self.alertLabel.setFont(QFont("JetBrains Mono NL"))
        #self.alertLabel.setText(alertData)
        #self.alertLabel.setWordWrap(True)
        #self.alertLabel.resize(250, 150)
        #self.alertLabel.move(200, 20)
        self.exec_()

    def calculateCorner(self):
        # I took this from stackoverflow (mostly)
        # https://stackoverflow.com/questions/39046059/pyqt-location-of-the-window
        maxGeo = QDesktopWidget().availableGeometry()
        primeGeo = QDesktopWidget().screenGeometry()

        windowGeometry = self.geometry()
        x = maxGeo.width() - self.width()
        y = 2 * maxGeo.height() - primeGeo.height() - self.height()
        self.move(x - 10, y)


class TabLayout():
    def coreLayout(self,tab,tWidget):
        tab.layout = QVBoxLayout(tWidget)

        tab.output = QPlainTextEdit(tab)
        tab.output.move(20, 20)
        tab.output.resize(1330, 350)
        tab.output.setStyleSheet("background-color: rgb(245, 245, 245);border: 1px solid rgb(223, 223, 224);")
        tab.output.setFont(QFont("JetBrains Mono NL"))
        tab.output.insertPlainText("[ Directive Output ]")
        tab.output.insertPlainText("\n")
        tab.output.insertPlainText("----------------------------------------------------------------------------------------------------------------------------------")

        tab.output.setReadOnly(True)

        tab.form = FormDefault(tab).formGroupBox
        tab.interface = InterfaceDefault(tab)

        return tab

    def consoleLayout(self, tab, tWidget):
        tab.layout = QVBoxLayout(tWidget)
        tab.label = QLabel(tab)
        tab.pixmapprim = QPixmap('..\\Lycanthropy_logo.png')
        tab.pixmap = tab.pixmapprim.scaledToHeight(300)
        tab.label.setPixmap(tab.pixmap)

        tab.label.resize(tab.pixmap.width(),
                         tab.pixmap.height())

        tab.wolfmon = QPlainTextEdit(tab)
        tab.wolfmon.move(300, 20)
        tab.wolfmon.resize(1050, 610)
        tab.wolfmon.setStyleSheet("background-color: rgb(245, 245, 245);border: 1px solid rgb(223, 223, 224);")
        tab.wolfmon.setFont(QFont("JetBrains Mono NL"))
        tab.wolfmon.insertPlainText("ACID      Campaign        Operating System                    User                   Integrity   Hostname")
        tab.wolfmon.insertPlainText("\n")
        tab.wolfmon.insertPlainText("----------------------------------------------------------------------------------------------------------------------------------")
        tab.wolfmon.setReadOnly(True)

        return tab.layout,tab.wolfmon

    def controlLayout(self, tab, tWidget):
        tab = self.coreLayout(tab,tWidget)
        return tab.layout,tab.output,tab.form

    def manageLayout(self, tab, tWidget):
        tab = self.coreLayout(tab,tWidget)
        return tab.layout,tab.output,tab.form

    def windowsLayout(self, tab, tWidget):
        tab = self.coreLayout(tab,tWidget)
        return tab.layout,tab.output,tab.form

    def posixLayout(self, tab, tWidget):
        tab = self.coreLayout(tab,tWidget)
        return tab.layout,tab.output,tab.form

    def shellHandlerLayout(self, tab, tWidget, session):
        tab.silentout = True
        tab.layout = QVBoxLayout(tWidget)
        tab.shellOut = QPlainTextEdit(tab)
        tab.shellMeta = QPlainTextEdit(tab)

        tab.shellCore = QWidget(tab)

        shellForm = QFormLayout()
        shellIn = QPlainTextEdit(tab)
        shellSelect = QLineEdit(tab)
        interpSelect = QComboBox(tab)
        runShell = QPushButton("Run")

        #output for shell
        tab.shellOut.move(500, 20)
        tab.shellOut.resize(850, 410)
        tab.shellOut.setStyleSheet("background-color: rgb(100,100,100);border: 1px solid rgb(223, 223, 224); color: rgb(255,255,255);")
        tab.shellOut.setFont(QFont("JetBrains Mono NL"))
        tab.shellOut.setReadOnly(True)
        
        #agent metadata feed
        tab.shellMeta.move(20, 20)
        tab.shellMeta.resize(450, 410)
        tab.shellMeta.setStyleSheet("background-color: rgb(245, 245, 245);border: 1px solid rgb(223, 223, 224);")
        tab.shellMeta.setFont(QFont("JetBrains Mono NL"))
        tab.shellMeta.insertPlainText("[ Agent Metadata ]")
        tab.shellMeta.insertPlainText("\n")
        tab.shellMeta.insertPlainText("------------------------------------------------------")
        tab.shellMeta.setReadOnly(True)

        #input for shell
        shellIn.setStyleSheet("background-color: rgb(100,100,100);border: 1px solid rgb(223, 223, 224); color: rgb(255,255,255);")
        shellIn.setFont(QFont("JetBrains Mono NL"))
        shellIn.setPlaceholderText("Shell command to run...")
        shellIn.setOverwriteMode(True)
        
        #agent select input
        shellSelect.setFont(QFont("JetBrains Mono NL"))
        shellSelect.setPlaceholderText("agent to interact with")

        #interpret select input
        interpSelect.setFont(QFont("JetBrains Mono NL"))
        interpSelect.addItem("/bin/bash")
        interpSelect.addItem("/bin/sh")
        interpSelect.addItem("python")
        interpSelect.addItem("powershell")
        interpSelect.addItem("cmd")

        #shellForm binding to qwidget

        tab.shellCore.setLayout(shellForm)
        tab.shellCore.resize(1330, 180)
        tab.shellCore.move(20,450)
        tab.shellCore.setStyleSheet("border: 1px solid rgb(223, 223, 224);")

        runShell.setFont(QFont("JetBrains Mono NL"))
        runShell.setFixedSize(100,30)
        runShell.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
        runShell.clicked.connect(lambda: btnCoreFunctions().shellConnect(shellSelect.text(), interpSelect.currentText(), shellIn.toPlainText().replace("[lycanthropy]::shell > ",""), shellIn, tab, session))

        shellForm.addRow(shellSelect)
        shellForm.addRow(interpSelect)
        shellForm.addRow(shellIn)
        shellForm.addRow(runShell)

        return tab.layout, tab.shellOut, shellForm, tab.shellMeta

    def fileHandlerLayout(self, tab, tWidget):

        return tab.layout, tab.output, tab.form

    def updateInterface(self, tabHandle, view, viewConfig,session):

        for directive in viewConfig[view]:
            self.mkTab(directive,tabHandle,view,session)


    def mkTab(self,name,subTab,view,session):
        #make tab for command
        #button1 = QPushButton(subTab)
        #button1.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
        #button1.resize(250,30)
        #button1.move(20,(counter * 35))
        #button1.setEnabled(True)
        #button1.setText(name)
        #button1.clicked.connect(lambda: (btnCoreFunctions().searchFor(view))(name,view,subTab))

        formTab = QWidget()
        tabLayout = QFormLayout()
        tabLayout.setLabelAlignment(Qt.AlignRight)
        formTab.setLayout(tabLayout)
        #formTab.setStyleSheet("background-color: rgb(245, 245, 245);border: 1px solid rgb(223, 223, 224);font: JetBrains MonoNL;")
        output = lycanthropy.ui.webClient.getGranularForm(
            name,
            view
        )
        self.mkForm(name, formTab, view, output.json(),tabLayout,session,subTab)
        subTab.form.addTab(formTab,name)


    def mkForm(self,name,subTab,view,form,layout,session,tabParent):
        #subTab.form
        formFields = {}
        subTab.setFont(QFont("JetBrains Mono NL"))
        dirLabel = QLabel(name)
        dirLabel.setFont(QFont("JetBrains Mono NL"))
        layout.addRow(dirLabel,None)

        for lineItem in form[name]:
            lineText = QLabel(lineItem)
            lineText.setFont(QFont("JetBrains Mono NL"))

            lineBox = QLineEdit()
            lineBox.setPlaceholderText(form[name][lineItem])
            lineBox.setFont(QFont("JetBrains Mono NL"))

            formFields[lineItem] = lineBox
            layout.addRow(lineText, lineBox)
        runButton = QPushButton('Run')
        runButton.setFixedSize(100,30)
        runButton.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
        #runButton.setStyleSheet("QPushButton::hover{background-color: red}")
        runButton.clicked.connect(lambda: btnCoreFunctions().runConnect(view,name,formFields,session,tabParent))
        layout.addRow(runButton)

        clearButton = QPushButton('Clear')
        clearButton.setFixedSize(100,30)
        clearButton.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
        clearButton.clicked.connect(lambda: btnCoreFunctions().clearConnect(tabParent))
        layout.addRow(clearButton)

class btnCoreFunctions():
    def __init__(self):
        self.viewCategories = {"control":"core","windows":"core","posix":"core","manage":"core","console":"meta"}
        self.viewMap = {"core":self.coreConnect,"meta":self.metaConnect}

    def coreConnect(self,name,view,subTab):
        #initializes the form which has a separate submit button
        #print("core")
        output = lycanthropy.ui.webClient.getGranularForm(
            name,
            view
        )
        TabLayout().mkForm(name,subTab,view,output.json())

    def metaConnect(self):
        print("meta")

    def runConnect(self,view,name,fields,session,subTab):
        session.form = {}
        session.form[name] = {}
        #if type(fields) == dict:
        #    session.form[name] = fields
        #else:
        for item in fields:
            if type(fields[item]) != str:
                session.form[name][item] = fields[item].text()
            else:
                session.form[name][item] = fields[item]

        runRes = lycanthropy.ui.directiveProcessor.process(
            "run",
            view,
            session
        )
        #lycanthropy.ui.util.chkModLocals(runRes[0], session)
        print("fields: {}".format(str(fields)))
        if type(fields) != dict:
            subTab.output.appendPlainText(runRes[0][0])
        else:
            if 'jobID' not in runRes[0][0]:
                subTab.output.appendPlainText(runRes[0][0])

    def shellConnect(self,acid,interpreter,command,inputObj, tab,session):
        inputObj.clear()
        inputObj.setPlaceholderText("Shell command to run...")
        self.runConnect("control","exec.command",{"shell":"SEJID","acid":acid,"interpreter":interpreter,"command":command},session,tab)

    def clearConnect(self,subTab):
        subTab.output.clear()
        subTab.output.insertPlainText("[ Directive Output ]")
        subTab.output.insertPlainText("\n")
        subTab.output.insertPlainText("----------------------------------------------------------------------------------------------------------------------------------")

    def searchFor(self,view):
        return self.viewMap[self.viewCategories[view]]
