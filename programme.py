import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import time,os

def start_flask_silently(script_path):
    subprocess.Popen(
        ["python", script_path],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

start_flask_silently("DERIVEE/derivee.pyw")
start_flask_silently("MATRICES/matrices.pyw")
start_flask_silently("SVM/SVM.pyw")

time.sleep(4)
with open("PID.dat","w") as f:
    f.write(str(os.getpid()))

app = QApplication(sys.argv)
tabs = QTabWidget()
tabs.setWindowTitle("Visualisation Machine Learning")
tabs.resize(1024, 768)

def make_tab(url):
    tab = QWidget()
    layout = QVBoxLayout()
    web = QWebEngineView()
    web.load(QUrl(url))
    layout.addWidget(web)
    tab.setLayout(layout)
    return tab

tabs.addTab(make_tab("http://127.0.0.1:5000"), "Régression linéaire avec descente gradient")
tabs.addTab(make_tab("http://127.0.0.1:5001"), "Régression linéaire avec matrices")
tabs.addTab(make_tab("http://127.0.0.1:5002"), "SVM")

tabs.show()
sys.exit(app.exec())
