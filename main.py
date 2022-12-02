
#URL GITHUB https://github.com/ValentinLong86/ControlProg

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import time
import threading
import socket


class MainWindows(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chronomètre")
        self.compteur = 0
        self.noAttempts = True
        self.connected = False
        
        widget = QWidget(self)
        grid = QGridLayout()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        labelCompteur = QLabel("Compteur :")
        self.lineEdit = QLineEdit(str(self.compteur))
        self.lineEdit.setDisabled(True)  # setReadOnly possible mais le lineEdit devait être grisé
        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start)
        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop)
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset)
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect)
        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.quit)

        grid.addWidget(labelCompteur, 0, 0)
        grid.addWidget(self.lineEdit, 1, 0, 1, 2)
        grid.addWidget(start_button, 2, 0, 1, 2)
        grid.addWidget(reset_button, 3, 0)
        grid.addWidget(stop_button, 3, 1)
        grid.addWidget(connect_button, 4, 0)
        grid.addWidget(quit_button, 4, 1)

    def start(self):
        self.compteur_thread = threading.Thread(target=self.__start)
        self.compteur_thread.start()

    def __start(self):
        self.noAttempts = False
        self.arret_thread = False

        if self.connected:
            try:
                msg = "start"
                self.client.send(msg.encode("utf-8"))
            except:
                print("Erreur")
                self.connected = False

        while self.arret_thread is False:
            self.compteur += 1
            self.lineEdit.setText(str(self.compteur))
            if self.connected:
                try:
                    msg = str(self.compteur)
                    self.client.send(msg.encode("utf-8"))
                except:
                    print("Erreur")
                    self.connected = False

            time.sleep(1)

        self.connected = True
        self.compteur = 0
        self.lineEdit.setText(str(self.compteur))

    def stop(self):
        if self.connected:
            try:
                msg = "stop"
                self.client.send(msg.encode("utf-8"))
            except:
                self.serverIsDisconnectedDialogBox()
                self.connected = False

        self.arret_thread = True
        self.compteur_thread.join()

    def reset(self):
        if self.connected:
            try:
                msg = "reset"
                self.client.send(msg.encode("utf-8"))
            except:
                self.serverIsDisconnectedDialogBox()
                self.connected = False
        
        self.stop()

    def connect(self):
        host = "127.0.0.1"
        port = 10000

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except:
            self.msgBox = QMessageBox(self)
            self.msgBox.setText("Une erreur s'est produite")
            self.msgBox.setWindowTitle("Erreur")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()      
            return -1

        msg = "connect"
        self.client.send(msg.encode("utf-8"))

    def quit(self):
        self.arret_thread = True

        if self.noAttempts is False:
            self.stop()

        if self.connected:
            try:
                msg = "bye"
                self.client.send(msg.encode("utf-8"))
            except:
                self.serverIsDisconnectedDialogBox()
                self.connected = False

        QApplication.exit(0)

    def serverIsDisconnectedDialogBox(self):
        self.msgBox = QMessageBox(self)
        self.msgBox.setText("La connexion avec le serveur à été perdue")
        self.msgBox.setWindowTitle("Erreur")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.show()

if __name__ == "__main__":
    application = QApplication(sys.argv)
    windows = MainWindows()
    windows.show()
    application.exec()