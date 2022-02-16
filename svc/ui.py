import threading

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFont
import sys
import lycanthropy.ui.graphic
import lycanthropy.daemon.util
import lycanthropy.ui.webClient
import lycanthropy.ui.connectors

wolfmonHandle = None
controlHandle = None
sessionHandle = None
monitorHanlde = None
shellHandle = None

class LoginControl(QDialog):
    def __init__(self,parent=None):
        super(LoginControl, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.setWindowTitle("Lycanthropy UI")

        self.label = QLabel(self)
        self.pixmapprim = QPixmap('..\\Lycanthropy_logo.png')
        self.pixmap = self.pixmapprim.scaledToHeight(300)
        self.label.setPixmap(self.pixmap)

        self.label.resize(self.pixmap.width(),
                         self.pixmap.height())

        self.labelUser = QLabel(self)
        self.labelUser.setText("User: ")
        self.labelUser.move(20,300)

        self.labelPass = QLabel(self)
        self.labelPass.setText("Pass: ")
        self.labelPass.move(20,350)

        self.username = QLineEdit(self)
        self.username.setFont(QFont("JetBrains Mono NL"))
        self.username.move(70,300)
        self.username.resize(200,30)

        self.password = QLineEdit(self)
        self.password.setFont(QFont("JetBrains Mono NL"))
        self.password.setEchoMode(QLineEdit.Password)
        self.password.move(70,350)
        self.password.resize(200,30)

        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
        self.buttonLogin.move(65,400)

        self.buttonExit = QPushButton('Close',self)
        self.buttonExit.setStyleSheet("QPushButton{border-radius: 15px;border: 1px solid rgb(125, 125, 125);}QPushButton::pressed{border-radius: 15px;border: 1px solid rgb(88, 88, 88); background-color: rgb(245,245,245)}")
        self.buttonExit.move(170,400)
        self.setWindowIcon(QIcon("../lycan_transparent.png"))

        self.buttonLogin.clicked.connect(self.handleLogin)
        self.resize(300,450)

        #layout.addWidget(self.username)
        #layout.addWidget(self.password)
        #layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        global sessionHandle

        #login code
        loginStatus,sessionHandle = lycanthropy.ui.connectors.ui().authenticate(self.username.text(), self.password.text())
        if loginStatus == True:
            self.accept()
        else:
            self.username.setText("")
            self.password.setText("")



class TabInset(QWidget):
    
    def __init__(self, parent):
        global wolfmonHandle
        global controlHandle
        global windowsHandle
        global posixHandle
        global manageHandle
        global shellHandle

        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.console = QWidget()
        self.control = QWidget()
        self.manage = QWidget()
        self.windows = QWidget()
        self.posix = QWidget()
        self.shell = QWidget()
        self.tabs.resize(610,200)



        # Add tabs
        self.tabs.addTab(self.console,"console")
        self.tabs.addTab(self.control,"control")
        self.tabs.addTab(self.manage,"manage")
        self.tabs.addTab(self.windows,"windows")
        self.tabs.addTab(self.posix,"posix")
        self.tabs.addTab(self.shell,"shell")

        self.shell.layout, self.shell.output, self.shell.form, self.shell.metadata = lycanthropy.ui.graphic.TabLayout().shellHandlerLayout(self.shell,self,sessionHandle)
        self.shell.setLayout(self.shell.layout)
        shellHandle = self.shell

        self.console.layout,self.console.wolfmon = lycanthropy.ui.graphic.TabLayout().consoleLayout(self.console,self)
        self.console.setLayout(self.console.layout)
        wolfmonHandle = self.console

        self.control.layout,self.control.output,self.control.form = lycanthropy.ui.graphic.TabLayout().controlLayout(self.control,self)
        self.control.setLayout(self.control.layout)
        controlHandle = self.control
        
        self.manage.layout,self.manage.output,self.manage.form = lycanthropy.ui.graphic.TabLayout().manageLayout(self.manage,self)
        self.manage.setLayout(self.manage.layout)
        manageHandle = self.manage
        
        self.windows.layout,self.windows.output,self.windows.form = lycanthropy.ui.graphic.TabLayout().windowsLayout(self.windows,self)
        self.windows.setLayout(self.windows.layout)
        windowsHandle = self.windows
        
        self.posix.layout,self.posix.output,self.posix.form = lycanthropy.ui.graphic.TabLayout().posixLayout(self.posix,self)
        self.posix.setLayout(self.posix.layout)
        posixHandle = self.posix
        
        # Create first tab
        #self.tab1.layout = QVBoxLayout(self)
        #self.pushButton1 = QPushButton("PyQt5 button")
        #self.tab1.layout.addWidget(self.pushButton1)
        #self.tab1.setLayout(self.tab1.layout)


        #threading.Thread(target=lycanthropy.ui.connectors.startMonitorThread, args=(sessionHandle,{"wolfmon":wolfmonHandle,"control":controlHandle,"manage":manageHandle,"windows":windowsHandle,"posix":posixHandle},))
        #lycanthropy.ui.connectors.startMonitorThread(sessionHandle,{"wolfmon":wolfmonHandle,"control":controlHandle,"manage":manageHandle,"windows":windowsHandle,"posix":posixHandle})

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.alertDataBox = QPlainTextEdit(self)
        self.alertDataBox.move(32, 680)
        self.alertDataBox.resize(1333,190)
        self.alertDataBox.setStyleSheet("background-color: rgb(245, 245, 245);border: 1px solid rgb(223, 223, 224);")
        self.alertDataBox.setFont(QFont("JetBrains Mono NL"))
        self.alertDataBox.insertPlainText("[ Agent Activity Alerts ]")
        self.alertDataBox.insertPlainText("\n")
        self.alertDataBox.insertPlainText("----------------------------------------------------------------------------------------------------------------------------------------------")
        self.alertDataBox.insertPlainText("\n")
        self.alertDataBox.setReadOnly(True)
        lycanthropy.ui.connectors.initWolfmon(sessionHandle, {"alerts":self.alertDataBox,"shell":shellHandle, "wolfmon":wolfmonHandle, "control":controlHandle, "manage":manageHandle, "windows":windowsHandle, "posix":posixHandle})
        lycanthropy.ui.webClient.monitorApiInit()
        self.setLayout(self.layout)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.acceptDrops()
        self.setWindowTitle("Lycanthropy UI")

        self.tabnav = TabInset(self)
        self.setCentralWidget(self.tabnav)
        self.setFixedSize(1400, 900)
        self.setWindowIcon(QIcon("../lycan_transparent.png"))

        self.show()

    def closeEvent(self,event):
        lycanthropy.ui.util.modLocals(None,sessionHandle)



# create pyqt5 app
App = QApplication(sys.argv)
dir_ = QDir("../etc/JetBrainsMono-2.225")
_id = QFontDatabase.addApplicationFont("../etc/JetBrainsMono-2.225/fonts/ttf/JetBrainsMonoNL-Regular.ttf")
print(QFontDatabase.applicationFontFamilies(_id))

login = LoginControl()
if login.exec() == QDialog.Accepted:


    # create the instance of our Window
    window = Window()
    #test output
    #wolfmonHandle.insertPlainText("0A1F265   WARFIEND        Windows[x64]                test                   low         WinXServ")
  
    # start the app
    sys.exit(App.exec())