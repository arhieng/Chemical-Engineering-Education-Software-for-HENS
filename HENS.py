import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from MER import DataStream
from MER import GridMer
from MER import MerCalc
from MER import merSoltoText


class MainWindows(QMainWindow):
    def __init__(self,
                 parent=None):
        super(MainWindows, self).__init__(parent)

        self.setWindowTitle("Heat Exchanger Network Synthesis - UNIVERSITAS RIAU")
        self.resize(1280, 1024)

        # Frame in MainWindows
        self.frame01 = QGroupBox("Number of Stream", self)
        self.frame01.setGeometry(25, 15, 100, 80)

        self.frame02 = QGroupBox("Data Stream", self)
        self.frame02.setGeometry(25, 100, 220, 560)

        self.frame03 = QGroupBox("ΔT min", self)
        self.frame03.setGeometry(175, 15, 70, 50)
        self.frame03.setAlignment(Qt.AlignCenter)

        self.frame04 = QGroupBox("Target MER", self)
        self.frame04.setGeometry(905, 15, 340, 85)
        self.frame04.setAlignment(Qt.AlignCenter)

        self.frame05 = QGroupBox("Grid Diagram", self)
        self.frame05.setGeometry(255, 100, 990, 780)

        # add number of stream widget in frame01
        # Hot Stream
        self.w_numberofStream = QWidget(self)
        self.w_numberofStream.setGeometry(25, 20, 100, 80)
        self.l_numberofStream = QGridLayout(self.w_numberofStream)
        self.l_numberofStream.setVerticalSpacing(0)
        self.labelHot = QLabel("Hot")
        self.numberofStreamH = QSpinBox()
        self.numberofStreamH.setRange(0, 20)
        # Cold Stream
        self.labelCold = QLabel("Cold")
        self.numberofStreamC = QSpinBox()
        self.numberofStreamC.setRange(0, 20)
        # add Widget to layout
        self.l_numberofStream.addWidget(self.labelHot, 0, 0)
        self.l_numberofStream.addWidget(self.numberofStreamH, 0, 1)
        self.l_numberofStream.addWidget(self.labelCold, 1, 0)
        self.l_numberofStream.addWidget(self.numberofStreamC, 1, 1)
        self.w_numberofStream.setLayout(self.l_numberofStream)
        # add Button for add Table Cell
        self.addBtn = QPushButton("add", self)
        self.addBtn.setGeometry(130, 20, 40, 75)
        self.addBtn.clicked.connect(self.add_row)

        # table input widget in frame02
        self.w_tableInput = QWidget(self)
        self.w_tableInput.setGeometry(25, 110, 220, 550)
        self.l_tableInput = QVBoxLayout(self.w_tableInput)
        # Hot Stream
        self.tableInputH = QTableWidget()
        self.tableInputH.setColumnCount(4)
        self.tableInputH.setRowCount(0)
        self.tableInputH.setHorizontalHeaderLabels(['Hot', 'Ts', 'Tt', 'C'])
        self.tableInputH.verticalHeader().setVisible(False)
        self.tableInputH.horizontalHeader().setDefaultSectionSize(50)
        self.tableInputH.verticalHeader().setDefaultSectionSize(25)
        self.style = "::section {""background-color: rgb(200, 200, 200); }"
        self.tableInputH.horizontalHeader().setStyleSheet(self.style)
        self.tableInputH.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableInputH.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Cold Stream
        self.tableInputC = QTableWidget()
        self.tableInputC.setColumnCount(4)
        self.tableInputC.setRowCount(0)
        self.tableInputC.setHorizontalHeaderLabels(['Cold', 'Ts', 'Tt', 'C'])
        self.tableInputC.verticalHeader().setVisible(False)
        self.tableInputC.horizontalHeader().setDefaultSectionSize(50)
        self.tableInputC.verticalHeader().setDefaultSectionSize(25)
        self.style = "::section {""background-color: rgb(200, 200, 200); }"
        self.tableInputC.horizontalHeader().setStyleSheet(self.style)
        self.tableInputC.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableInputC.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # add table widget to layout
        self.l_tableInput.addWidget(self.tableInputH)
        self.l_tableInput.addWidget(self.tableInputC)

        # ΔT min input in frame03
        self.dTminInput = QLineEdit(self)
        self.dTminInput.setGeometry(185, 35, 50, 20)
        self.dTminInput.setAlignment(Qt.AlignCenter)

        # Target MER value in frame04
        self.w_targetMer = QWidget(self)
        self.w_targetMer.setGeometry(915, 20, 320, 80)
        self.l_targetMer = QGridLayout(self.w_targetMer)
        self.l_targetMer.setVerticalSpacing(0)
        self.l_targetMer.setHorizontalSpacing(10)
        self.TPH = QLabel("T Pinch Hot")
        self.TPH.setAlignment(Qt.AlignCenter)
        self.TPC = QLabel("T Pinch Cold")
        self.TPC.setAlignment(Qt.AlignCenter)
        self.QHm = QLabel("Q Hot min")
        self.QHm.setAlignment(Qt.AlignCenter)
        self.QCm = QLabel("Q Cold min")
        self.QCm.setAlignment(Qt.AlignCenter)
        self.TPH_show = QLabel()
        self.TPH_show.setAlignment(Qt.AlignCenter)
        self.TPH_show.setStyleSheet("background-color: rgba(255, 255, 255, 0.50); border: 1px solid grey")
        self.TPC_show = QLabel()
        self.TPC_show.setAlignment(Qt.AlignCenter)
        self.TPC_show.setStyleSheet("background-color: rgba(255, 255, 255, 0.50); border: 1px solid grey")
        self.QHm_show = QLabel()
        self.QHm_show.setAlignment(Qt.AlignCenter)
        self.QHm_show.setStyleSheet("background-color: rgba(255, 255, 255, 0.50); border: 1px solid grey")
        self.QCm_show = QLabel()
        self.QCm_show.setAlignment(Qt.AlignCenter)
        self.QCm_show.setStyleSheet("background-color: rgba(255, 255, 255, 0.50); border: 1px solid grey")
        self.l_targetMer.addWidget(self.TPH, 0, 0)
        self.l_targetMer.addWidget(self.TPC, 0, 1)
        self.l_targetMer.addWidget(self.QHm, 0, 2)
        self.l_targetMer.addWidget(self.QCm, 0, 3)
        self.l_targetMer.addWidget(self.TPH_show, 1, 0)
        self.l_targetMer.addWidget(self.TPC_show, 1, 1)
        self.l_targetMer.addWidget(self.QHm_show, 1, 2)
        self.l_targetMer.addWidget(self.QCm_show, 1, 3)
        self.w_targetMer.setLayout(self.l_targetMer)

        # Grid Diagram Show in Frame05
        self.w_gridD = QWidget(self)
        self.w_gridD.setGeometry(265, 120, 970, 750)
        self.w_gridD.setStyleSheet("background-color: rgba(255, 255, 255, 0.50); border: 1px solid grey")
        self.l_gridD = QFormLayout(self.w_gridD)
        self.l_gridD.setAlignment(Qt.AlignCenter)
        self.w_gridD.setLayout(self.l_gridD)

        # Process Button for show value
        self.processBtn = QPushButton("Process", self)
        self.processBtn.setGeometry(180, 665, 65, 25)
        self.processBtn.clicked.connect(self.procees_data)

    def add_row(self):
        self.tableInputH.setRowCount(self.numberofStreamH.value())
        self.tableInputC.setRowCount(self.numberofStreamC.value())

    def procees_data(self):
        # ΔT min input variable to process
        dTm = float(self.dTminInput.text())

        # data Hot Stream process
        dataHot = []
        for hrow in range(self.numberofStreamH.value()):
            strNameH = self.tableInputH.item(hrow, 0).text()
            tempSourceH = float(self.tableInputH.item(hrow, 1).text())
            tempTargetH = float(self.tableInputH.item(hrow, 2).text())
            CpH = float(self.tableInputH.item(hrow, 3).text())

            H = DataStream(tempSourceH, tempTargetH, CpH, strNameH)
            dataHot.append(H)

        # data Cold Stream process
        dataCold = []
        for crow in range(self.numberofStreamC.value()):
            strNameC = self.tableInputC.item(crow, 0).text()
            tempSourceC = float(self.tableInputC.item(crow, 1).text())
            tempTargetC = float(self.tableInputC.item(crow, 2).text())
            CpC = float(self.tableInputC.item(crow, 3).text())

            C = DataStream(tempSourceC, tempTargetC, CpC, strNameC)
            dataCold.append(C)

        self.mer = MerCalc(dataHot, dataCold, dTm)
        solutionText = merSoltoText(self.mer)
        print(solutionText)

        # Show Target MER in MainWindows
        Q_Hm = str(self.mer.qHmin)
        T_PC = str(self.mer.tPinchCold)
        T_PH = str(self.mer.tPinchHot)
        Q_Cm = str(self.mer.qCmin)

        self.TPH_show.setText(T_PH)
        self.TPC_show.setText(T_PC)
        self.QHm_show.setText(Q_Hm)
        self.QCm_show.setText(Q_Cm)
        self.gridMer = GridMer(self.mer)
        self.none = QWidget()
        self.none.setFixedSize(970, 750)
        self.none.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.l_gridD.addWidget(self.none)
        self.l_gridD.removeWidget(self.none)
        self.l_gridD.addWidget(self.gridMer)
        self.l_gridD.removeWidget(self.gridMer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindows()
    ex.show()
    sys.exit(app.exec_())
