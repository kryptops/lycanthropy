from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
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

    #def mkButton(self,name,subTab):
    #    button1 = QPushButton(subTab)
    #    button1.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
    #    button1.resize(250,30)
    #    button1.move(20,30)
    #    button1.setEnabled(True)
    #    button1.setText(name)
    #    button1.clicked.connect(self.execCommand)
    #    self.buttonSet[name] = button1

    #def parseDirectives(self):
    #    pass

    #def execCommand(self):
    #    print("Button 1 clicked")


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
        tab.wolfmon.insertPlainText("ACID      Campaign        Operating System            User                   Integrity   Hostname")
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
            #formRow = QLineEdit()
            lineText = QLabel(lineItem)
            #QLabel.setStyleSheet()
            lineText.setFont(QFont("JetBrains Mono NL"))
            lineBox = QLineEdit(form[name][lineItem])
            lineBox.setFont(QFont("JetBrains Mono NL"))
            formFields[lineItem] = lineBox
            layout.addRow(lineText, lineBox)
        runButton = QPushButton('Run')
        #runButton.setStyleSheet("QPushButton::hover{background-color: red}")
        runButton.clicked.connect(lambda: btnCoreFunctions().runConnect(view,name,formFields,session,tabParent))
        layout.addRow(runButton)

        clearButton = QPushButton('Clear')
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
        for item in fields:
            session.form[name][item] = fields[item].text()
        runRes = lycanthropy.ui.directiveProcessor.process(
            "run",
            view,
            session
        )[0][0]
        subTab.output.appendPlainText(runRes)


    def clearConnect(self,subTab):
        subTab.output.clear()
        subTab.output.insertPlainText("[ Directive Output ]")
        subTab.output.insertPlainText("\n")
        subTab.output.insertPlainText("----------------------------------------------------------------------------------------------------------------------------------")

    def searchFor(self,view):
        return self.viewMap[self.viewCategories[view]]
