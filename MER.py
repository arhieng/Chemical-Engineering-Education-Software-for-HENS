class DataStream:
    """docstring for """

    def __init__(self, ts, tt, c, name):
        self.ts = ts
        self.tt = tt
        self.c = c
        self.name = name


class StreamGrid(DataStream):
    """docstring for """

    def __init__(self, ts, tt, c, name):
        super().__init__(ts, tt, c, name)
        self.heat = abs(ts - tt) * c
        self.heatRemaining = self.heat
        self.matchTarget = False
        self.haveMatch = False

    def addHeatIn(self, heatIn):
        self.heatRemaining = self.heatRemaining - heatIn
        if self.heatRemaining == 0.0:
            self.matchTarget = True
        self.haveMatch = True


class MatchData:
    """MatchData hold information about macthing data"""

    def __init__(self, matchFrom, matchTo, heatLoad, besidePinch):
        self.matchFrom = matchFrom
        self.matchTo = matchTo
        self.heatLoad = heatLoad
        self.besidePinch = besidePinch


class MerCalc(object):

    def __init__(self,
                 dataHotStream: [DataStream],
                 dataColdStream: [DataStream],
                 dTmin: float):
        """ Constructor for Mer Calculation
        Keyword arguments:
        dataHotStream -- is a list of DataStream type Hot Stream
        dataColdStream -- is a list of DataStream type Cold Stream
        """
        self.dataHotStream = dataHotStream
        self.dataColdStream = dataColdStream
        self.streamHotInColdSide: list[StreamGrid] = []
        self.streamHotInHotSide: list[StreamGrid] = []
        self.streamColdInHotSide: list[StreamGrid] = []
        self.streamColdInColdSide: list[StreamGrid] = []
        # Calculate number of Stream in each data stream
        self.nHotStream = len(self.dataHotStream)
        self.nColdStream = len(self.dataColdStream)
        self.dTmin = dTmin
        self.calculate()
        self.streamMatch()

    def calculate(self):
        """ menyalin data temperatur masing-2 aliran ke intervalT """
        intervalT = []
        for _ in self.dataHotStream:
            intervalT.append(_.ts - self.dTmin)
            intervalT.append(_.tt - self.dTmin)
        for _ in self.dataColdStream:
            intervalT.append(_.ts)
            intervalT.append(_.tt)
        # remove redundant temperature in intervalT
        intervalT = list(set(intervalT))
        intervalT.sort()
        intervalT.reverse()
        listdT = []
        for i in range(len(intervalT) - 1):
            listdT.append(intervalT[i] - intervalT[i + 1])
        # cek temperature interval interception with data stream temperature interval
        listCP = []
        sumCpHot = 0.0
        sumCpCold = 0.0
        for i in range(len(intervalT) - 1):
            for j in range(len(self.dataHotStream)):
                # for data hot ts > tt
                if self.dataHotStream[j].ts - self.dTmin >= intervalT[i] > self.dataHotStream[j].tt - self.dTmin:
                    sumCpHot = sumCpHot + self.dataHotStream[j].c
            for k in range(len(self.dataColdStream)):
                # for data cold ts < tt
                if self.dataColdStream[k].tt >= intervalT[i] > self.dataColdStream[k].ts:
                    sumCpCold = sumCpCold + self.dataColdStream[k].c
            listCP.append(sumCpHot - sumCpCold)
            sumCpHot = 0.0
            sumCpCold = 0.0
        dH = []
        for i in range(len(listCP)):
            dH.append(listCP[i] * listdT[i])
        qcascadeInit = []
        sumQ = 0.0
        for i in range(len(dH)):
            sumQ = sumQ + dH[i]
            qcascadeInit.append(sumQ)
        qcascadeFinal = []
        qHmin = abs(min(qcascadeInit))
        qcascadeFinal.append(qHmin)
        sumQFinal = qHmin
        for i in range(len(qcascadeInit)):
            _ = qcascadeInit[i] + sumQFinal
            qcascadeFinal.append(_)
        qCmin = qcascadeFinal[len(qcascadeFinal) - 1]
        self.qCmin = qCmin
        self.qHmin = qHmin
        minValue = min(qcascadeFinal)
        index = qcascadeFinal.index(minValue)
        self.tPinchCold = intervalT[index]
        self.tPinchHot = self.tPinchCold + self.dTmin

    def streamMatch(self):
        # define stream Hot and Cold

        # Add stream grid in Hot Side
        for i in range(self.nHotStream):
            if self.dataHotStream[i].ts >= self.tPinchHot > self.dataHotStream[i].tt:
                self.streamHotInColdSide.append(
                    StreamGrid(self.tPinchHot, self.dataHotStream[i].tt, self.dataHotStream[i].c,
                               self.dataHotStream[i].name))
            elif self.tPinchHot > self.dataHotStream[i].ts:
                self.streamHotInColdSide.append(
                    StreamGrid(self.dataHotStream[i].ts, self.dataHotStream[i].tt, self.dataHotStream[i].c,
                               self.dataHotStream[i].name))
            if self.dataHotStream[i].tt <= self.tPinchHot < self.dataHotStream[i].ts:
                self.streamHotInHotSide.append(
                    StreamGrid(self.dataHotStream[i].ts, self.tPinchHot, self.dataHotStream[i].c,
                               self.dataHotStream[i].name))
            elif self.tPinchHot < self.dataHotStream[i].tt:
                self.streamHotInHotSide.append(
                    StreamGrid(self.dataHotStream[i].ts, self.dataHotStream[i].tt, self.dataHotStream[i].c,
                               self.dataHotStream[i].name))
        # Add Stream Grid in Cold Side
        for i in range(self.nColdStream):
            if self.dataColdStream[i].ts <= self.tPinchCold < self.dataColdStream[i].tt:
                self.streamColdInHotSide.append(
                    StreamGrid(self.tPinchCold, self.dataColdStream[i].tt, self.dataColdStream[i].c,
                               self.dataColdStream[i].name))
            elif self.tPinchCold < self.dataColdStream[i].ts:
                self.streamColdInHotSide.append(
                    StreamGrid(self.dataColdStream[i].ts, self.dataColdStream[i].tt, self.dataColdStream[i].c,
                               self.dataColdStream[i].name))
            if self.dataColdStream[i].tt >= self.tPinchCold > self.dataColdStream[i].ts:
                self.streamColdInColdSide.append(
                    StreamGrid(self.dataColdStream[i].ts, self.tPinchCold, self.dataColdStream[i].c,
                               self.dataColdStream[i].name))
            elif self.tPinchCold > self.dataColdStream[i].tt:
                self.streamColdInColdSide.append(
                    StreamGrid(self.dataColdStream[i].ts, self.dataColdStream[i].tt, self.dataColdStream[i].c,
                               self.dataColdStream[i].name))

        self.matchInColdSide = []
        self.matchInHotSide = []
        nameCold = ''
        nameHot = ''
        heatload = 0.0
        for streamHot in self.streamHotInColdSide:
            for streamCold in self.streamColdInColdSide:
                if streamHot.c >= streamCold.c:
                    if not nameCold == streamCold.name and not nameHot == streamHot.name:
                        if streamHot.heat <= streamCold.heat:
                            heatload = streamHot.heat
                        else:
                            heatload = streamCold.heat
                        streamHot.addHeatIn(heatload)
                        streamCold.addHeatIn(heatload)
                        self.matchInColdSide.append(MatchData(streamHot.name, streamCold.name, heatload, True))
                        nameHot = streamHot.name
                        nameCold = streamCold.name

        nameHot = ''
        nameCold = ''
        for streamHot in self.streamHotInHotSide:
            for streamCold in self.streamColdInHotSide:
                if streamHot.c <= streamCold.c:
                    if not nameHot == streamHot.name and not nameCold == streamCold.name:
                        if streamHot.heat <= streamCold.heat:
                            heatload = streamHot.heat
                        else:
                            heatload = streamCold.heat
                        streamHot.addHeatIn(heatload)
                        streamCold.addHeatIn(heatload)
                        self.matchInHotSide.append(MatchData(streamHot.name, streamCold.name, heatload, True))
                        nameHot = streamHot.name
                        nameCold = streamCold.name

        for streamHot in self.streamHotInColdSide:
            for streamCold in self.streamColdInColdSide:
                if not streamHot.matchTarget and not streamCold.matchTarget:
                    if streamHot.haveMatch or streamCold.haveMatch:
                        if streamHot.heatRemaining <= streamCold.heatRemaining:
                            heatload = streamHot.heatRemaining
                        else:
                            heatload = streamCold.heatRemaining
                        streamHot.addHeatIn(heatload)
                        streamCold.addHeatIn(heatload)
                        self.matchInColdSide.append(MatchData(streamHot.name, streamCold.name, heatload, False))

        for streamHot in self.streamHotInHotSide:
            for streamCold in self.streamColdInHotSide:
                if not streamHot.matchTarget and not streamCold.matchTarget:
                    if streamHot.haveMatch or streamCold.haveMatch:
                        if streamHot.heatRemaining <= streamCold.heatRemaining:
                            heatload = streamHot.heatRemaining
                        else:
                            heatload = streamCold.heatRemaining
                        streamHot.addHeatIn(heatload)
                        streamCold.addHeatIn(heatload)
                        self.matchInHotSide.append(MatchData(streamHot.name, streamCold.name, heatload, False))

    def printResult(self):
        # self._setIntervalT()
        print("Calculation Result of Maximum Energy Recovery Target")
        print("Data Input: ")
        print("--------------------------------------------------------------------")
        print("Stream Name" + "\t Ts" + "\t Tt" + "\t CP")
        print("--------------------------------------------------------------------")
        for _ in self.dataHotStream:
            print(str(_.name) + "\t\t" + str(_.ts) + "\t" + str(_.tt) + "\t" + str(_.c))
        for _ in self.dataColdStream:
            print(str(_.name) + "\t\t" + str(_.ts) + "\t" + str(_.tt) + "\t" + str(_.c))
        print("--------------------------------------------------------------------")
        print("Qh Minimum: " + str(self.qHmin))
        print("Qc Minimum: " + str(self.qCmin))
        print("T Pinch Hot: " + str(self.tPinchHot))
        print("T Pinch Cold: " + str(self.tPinchCold))
        print("--------------------------------------------------------------------")
        print()
        print("Solution to Grid Diagram")
        print("-------------------------")
        print("Match at Cold Side")
        print("Number of Match = " + str(len(self.matchInColdSide)))
        for match in self.matchInColdSide:
            print("Match from " + match.matchFrom + " To " + str(match.matchTo) + " Heat Load: " + str(match.heatLoad))
        for stream in self.streamHotInColdSide:
            if stream.heatRemaining > 0.0:
                print("Cold Utilities : " + str(stream.heatRemaining) + " at " + stream.name)
        print()
        print("Match at Hot Side")
        print("Number of Match = " + str(len(self.matchInHotSide)))
        for match in self.matchInHotSide:
            print("Match from " + match.matchFrom + " To " + str(match.matchTo) + " Heat Load: " + str(match.heatLoad))
        for stream in self.streamColdInHotSide:
            if stream.heatRemaining > 0.0:
                print("Hot Utilities : " + str(stream.heatRemaining) + " at " + stream.name)


def merSoltoText(mer: MerCalc) -> str:
    txt = "Calculation Result of Maximum Energy Recovery Target \n"
    txt = txt + "Data Input: \n"
    txt = txt + "--------------------------------\n"
    txt = txt + "Stream Name" + "\t Ts" + "\t\t Tt" + "\t\t CP \n"
    txt = txt + "--------------------------------\n"
    for _ in mer.dataHotStream:
        txt = txt + str(_.name) + "\t\t\t" + str(_.ts) + "\t\t" + str(_.tt) + "\t\t" + str(_.c) + "\n"
    for _ in mer.dataColdStream:
        txt = txt + str(_.name) + "\t\t\t" + str(_.ts) + "\t\t" + str(_.tt) + "\t\t" + str(_.c) + "\n"
    txt = txt + "--------------------------------\n"
    txt = txt + "Qh Minimum: " + str(mer.qHmin) + "\n"
    txt = txt + "Qc Minimum: " + str(mer.qCmin) + "\n"
    txt = txt + "T Pinch Hot: " + str(mer.tPinchHot) + "\n"
    txt = txt + "T Pinch Cold: " + str(mer.tPinchCold) + "\n"
    txt = txt + "--------------------------------\n"
    txt = txt + "\n"
    txt = txt + "Solution to Grid Diagram\n"
    txt = txt + "-------------------------\n"
    txt = txt + "Match at Cold Side\n"
    txt = txt + "Number of Match = " + str(len(mer.matchInColdSide)) + "\n"
    for match in mer.matchInColdSide:
        txt = txt + "Match from " + match.matchFrom + " To " + str(match.matchTo) + " Heat Load: " + str(match.heatLoad) + "\n"
    for stream in mer.streamColdInHotSide:
        if stream.heatRemaining > 0.0:
            txt = txt + "Hot Utilities : " + str(stream.heatRemaining) + " at " + stream.name + "\n"
    txt = txt + "\n"
    txt = txt + "Match at Hot Side\n"
    txt = txt + "Number of Match = " + str(len(mer.matchInHotSide)) + "\n"
    for match in mer.matchInHotSide:
        txt = txt + "Match from " + match.matchFrom + " To " + str(match.matchTo) + " Heat Load: " + str(match.heatLoad) + "\n"
    for stream in mer.streamHotInColdSide:
        if stream.heatRemaining > 0.0:
            txt = txt + "Cold Utilities : " + str(stream.heatRemaining) + " at " + stream.name + "\n"
    return txt


def test() -> MerCalc:

    h1 = DataStream(350, 160, 3.2, "h1")
    h2 = DataStream(400, 100, 3.0, "h2")
    h3 = DataStream(110, 60, 8.0, "h3")
    c1 = DataStream(50, 250, 4.5, "c1")
    c2 = DataStream(70, 320, 2.0, "c2")
    c3 = DataStream(100, 300, 3.0, "c3")
    datahot = [h1, h2, h3]
    datacold = [c1, c2, c3]
    mer = MerCalc(datahot, datacold, 10.0)
    return mer


class MerManager:
    def __init__(self, merCalc: MerCalc):
        self.mer = merCalc

    def init(self):
        pass


"""


Drawing MER Grid solution into PyQt5 widget


"""
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QPolygon
from PyQt5.QtWidgets import QWidget


def textSize(qp: QPainter, text: str):
    rect: QRect = QRect()
    rect = qp.boundingRect(rect, Qt.PlainText, text)
    textWidth = rect.width()
    textHeight = rect.height()
    return textWidth, textHeight


class StreamLine:
    def __init__(self, x1, y1, x2, y2, side: str, typeStream: str, streamGrid: StreamGrid):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.side = side
        self.typeStream = typeStream
        self.streamGrid = streamGrid
        self.name = self.streamGrid.name

    @staticmethod
    def drawArrow(qp: QPainter, x1, y1, x2, y2, x3, y3):
        points = QPolygon([
            QPoint(x1, y1),
            QPoint(x2, y2),
            QPoint(x3, y3)
        ])
        qp.drawPolygon(points)

    def drawStreamLine(self, qp: QPainter):
        ts = str(self.streamGrid.ts)
        tt = str(self.streamGrid.tt)
        ts_width, ts_height = textSize(qp, ts)
        tt_width, tt_height = textSize(qp, tt)

        if self.side == "hot" and self.typeStream == "hot":
            qp.setPen(QColor(Qt.red))
            qp.drawLine(self.x1, self.y1, self.x2, self.y2)
            qp.setBrush(QBrush(QColor(Qt.red)))
            self.drawArrow(qp, self.x2 - 10, self.y2 - 5,
                           self.x2, self.y2,
                           self.x2 - 10, self.y2 + 5)
            qp.drawText(self.x1, self.y1 - 2, ts)
            qp.drawText(self.x2 - tt_width - 10, self.y2 - 2, tt)

        if self.side == "hot" and self.typeStream == "cold":
            qp.setPen(QColor(Qt.blue))
            qp.drawLine(self.x1, self.y1, self.x2, self.y2)
            qp.setBrush(QBrush(QColor(Qt.blue)))
            self.drawArrow(qp, self.x2 + 10, self.y2 - 5,
                           self.x2, self.y2,
                           self.x2 + 10, self.y2 + 5)
            qp.drawText(self.x1 - ts_width, self.y1 - 2, ts)
            qp.drawText(self.x2 + 10, self.y2 - 2, tt)

        if self.side == "cold" and self.typeStream == "hot":
            qp.setPen(QColor(Qt.red))
            qp.drawLine(self.x1, self.y1, self.x2, self.y2)
            qp.setBrush(QBrush(QColor(Qt.red)))
            self.drawArrow(qp, self.x2 - 10, self.y2 - 5,
                           self.x2, self.y2,
                           self.x2 - 10, self.y2 + 5)
            qp.drawText(self.x1, self.y1 - 2, ts)
            qp.drawText(self.x2 - tt_width - 10, self.y2 - 2, tt)

        if self.side == "cold" and self.typeStream == "cold":
            qp.setPen(QColor(Qt.blue))
            qp.drawLine(self.x1, self.y1, self.x2, self.y2)
            self.drawArrow(qp, self.x2 + 10, self.y2 - 5,
                           self.x2, self.y2,
                           self.x2 + 10, self.y2 + 5)
            qp.drawText(self.x1 - ts_width, self.y1 - 2, ts)
            qp.drawText(self.x2 + 10, self.y2 - 2, tt)


class DrawGridSolution:
    def __init__(self, merCalc: MerCalc, width, height):
        self.mer = merCalc
        self.lineColdInColdSide: list[StreamLine] = []
        self.lineHotInColdSide: list[StreamLine] = []
        self.lineColdInHotSide: list[StreamLine] = []
        self.lineHotInHotSide: list[StreamLine] = []

        self.width = width
        self.height = height

        self.vspace = 40
        self.hspace = 60
        self.spaceAtPinch = 10

        self.circleDia = 20

        self.prepareData()

    def prepareData(self):
        # calculate height area for drawing grid mer
        nStream = len(self.mer.dataColdStream) + len(self.mer.dataHotStream)
        self.heightArea = self.vspace * (nStream + 1)

        # calculate width area for drawing grid mer
        nMatchInColdSide = len(self.mer.matchInColdSide)
        nMatchInHotSide = len(self.mer.matchInHotSide)
        nMatch = nMatchInColdSide + nMatchInHotSide
        self.widthArea = self.hspace * (nMatch + 5) + self.spaceAtPinch

        # finding pinch line position
        lengthXinColdSide = self.hspace * (nMatchInColdSide + 3)
        lengthXinHotSide = self.hspace * (nMatchInHotSide + 2)
        self.startXHotSide = lengthXinHotSide
        self.endXHotSide = 0
        self.startXColdSide = lengthXinHotSide + self.spaceAtPinch
        self.endXColdSide = self.startXColdSide + lengthXinColdSide - self.hspace

    def drawCircle(self, qp: QPainter, xpos, ypos, typeCircle: str):
        """
        draw circle dimana titik referensi atau posisi merupakan center dari circle
        """
        if typeCircle == "heat":
            qp.setPen(QColor(Qt.gray))
            qp.setBrush(QBrush(QColor(Qt.gray)))
        elif typeCircle == "coldUtil":
            qp.setPen(QColor(Qt.blue))
            qp.setBrush(QBrush(QColor(Qt.blue)))
        elif typeCircle == "hotUtil":
            qp.setPen(QColor(Qt.red))
            qp.setBrush(QBrush(QColor(Qt.red)))
        x = xpos - self.circleDia / 2
        y = ypos - self.circleDia / 2
        qp.drawEllipse(x, y, self.circleDia, self.circleDia)

    def drawColdUtil(self, qp: QPainter, i: int, endXColdSide, space):
        if self.mer.streamHotInColdSide[i].heatRemaining > 0:
            x = endXColdSide - self.hspace
            y = space
            self.drawCircle(qp, x, y, "coldUtil")
            qp.setPen(QColor(Qt.black))
            strColdUtil = str(self.mer.streamHotInColdSide[i].heatRemaining)
            textWidth, textHeight = textSize(qp, strColdUtil)
            textPosX = x - textWidth / 2
            textPosY = y + self.circleDia + 2
            qp.drawText(textPosX, textPosY, strColdUtil)

    def drawHotUtil(self, qp: QPainter, i: int, endXHotSide, space):
        if self.mer.streamColdInHotSide[i].heatRemaining > 0:
            x = endXHotSide + self.hspace
            y = space
            self.drawCircle(qp, x, y, "hotUtil")
            qp.setPen(QColor(Qt.black))
            strHotUtil = str(self.mer.streamColdInHotSide[i].heatRemaining)
            textWidth, textHeight = textSize(qp, strHotUtil)
            textPosX = x - textWidth / 2
            textPosY = y + self.circleDia + 2
            qp.drawText(textPosX, textPosY, strHotUtil)

    def drawLineMatch(self, qp: QPainter, x, y1, y2, match):
        qp.drawLine(x, y1, x, y2)
        self.drawCircle(qp, x, y1, "heat")
        self.drawCircle(qp, x, y2, "heat")
        string = str(match.heatLoad)
        twidth, theigh = textSize(qp, string)
        qp.setPen(QColor(Qt.black))
        qp.drawText(x - twidth / 2, y2 + self.circleDia, string)

    def drawGS(self, qp: QPainter):
        qp.drawLine(self.startXHotSide, 0, self.startXHotSide, self.heightArea)
        qp.drawLine(self.startXColdSide, 0, self.startXColdSide, self.heightArea)
        i = 0
        space = 0
        # draw hot stream line in cold side
        for streamHot in self.mer.dataHotStream:
            space = space + self.vspace
            if i < len(self.mer.streamHotInColdSide):
                if streamHot.name == self.mer.streamHotInColdSide[i].name:
                    if self.mer.streamHotInColdSide[i].ts == self.mer.tPinchHot:
                        streamLine = StreamLine(
                            self.startXColdSide, space,
                            self.endXColdSide, space,
                            "cold", "hot",
                            self.mer.streamHotInColdSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineHotInColdSide.append(streamLine)
                        self.drawColdUtil(qp, i, self.endXColdSide, space)
                        i = i + 1
                    else:
                        streamLine = StreamLine(
                            self.startXColdSide + self.hspace, space,
                            self.endXColdSide, space,
                            "cold", "hot",
                            self.mer.streamHotInColdSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineHotInColdSide.append(streamLine)
                        self.drawColdUtil(qp, i, self.endXColdSide, space)
                        i = i + 1
        # draw cold stream line in cold side
        i = 0
        for streamCold in self.mer.dataColdStream:
            space = space + self.vspace
            if i < len(self.mer.streamColdInColdSide):
                if streamCold.name == self.mer.streamColdInColdSide[i].name:
                    if self.mer.streamColdInColdSide[i].tt == self.mer.tPinchCold:
                        streamLine = StreamLine(self.endXColdSide, space, self.startXColdSide, space, "cold", "cold",
                                                self.mer.streamColdInColdSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineColdInColdSide.append(streamLine)
                        i = i + 1
                    else:
                        streamLine = StreamLine(
                            self.endXColdSide, space, self.startXColdSide + self.hspace, space, "cold", "cold",
                            self.mer.streamColdInColdSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineColdInColdSide.append(streamLine)
                        i = i + 1
        # draw hot stream line in hot side
        i = 0
        space = 0
        for streamHot in self.mer.dataHotStream:
            space = space + self.vspace
            if i < len(self.mer.streamHotInHotSide):
                if streamHot.name == self.mer.streamHotInHotSide[i].name:
                    if self.mer.streamHotInHotSide[i].tt == self.mer.tPinchHot:
                        streamLine = StreamLine(
                            self.endXHotSide, space, self.startXHotSide, space, "hot", "hot",
                            self.mer.streamHotInHotSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineHotInHotSide.append(streamLine)
                        i = i + 1
                    else:
                        streamLine = StreamLine(
                            self.endXHotSide, space, self.startXHotSide - 20, space, "hot", "hot",
                            self.mer.streamHotInHotSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineHotInHotSide.append(streamLine)
                        i = i + 1
        # draw cold line in hot side
        i = 0
        for streamCold in self.mer.dataColdStream:
            space = space + self.vspace
            if i < len(self.mer.streamColdInHotSide):
                if streamCold.name == self.mer.streamColdInHotSide[i].name:
                    if self.mer.streamColdInHotSide[i].ts == self.mer.tPinchCold:
                        streamLine = StreamLine(
                            self.startXHotSide, space, self.endXHotSide, space, "hot", "cold",
                            self.mer.streamColdInHotSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineColdInHotSide.append(streamLine)
                        self.drawHotUtil(qp, i, self.endXHotSide, space)
                        i = i + 1
                    else:
                        streamLine = StreamLine(
                            self.startXHotSide - self.hspace, space,
                            self.endXHotSide, space,
                            "hot", "cold",
                            self.mer.streamColdInHotSide[i])
                        streamLine.drawStreamLine(qp)
                        self.lineColdInHotSide.append(streamLine)
                        self.drawHotUtil(qp, i, self.endXHotSide, space)
                        i = i + 1
        # draw stream matching in solution grid
        x = self.startXColdSide + self.hspace
        for match in self.mer.matchInColdSide:
            matchFrom = match.matchFrom
            matchTo = match.matchTo
            for lineHot in self.lineHotInColdSide:
                if matchFrom == lineHot.name:
                    y1 = lineHot.y1
                    for lineCold in self.lineColdInColdSide:
                        if lineCold.name == matchTo:
                            y2 = lineCold.y1
                            self.drawLineMatch(qp, x, y1, y2, match)
            x = x + self.hspace
        x = self.startXHotSide - self.hspace
        for match in self.mer.matchInHotSide:
            matchFrom = match.matchFrom
            matchTo = match.matchTo
            for lineHot in self.lineHotInHotSide:
                if matchFrom == lineHot.name:
                    y1 = lineHot.y1
                    for lineCold in self.lineColdInHotSide:
                        if lineCold.name == matchTo:
                            y2 = lineCold.y1
                            self.drawLineMatch(qp, x, y1, y2, match)
            x = x - self.hspace


class GridMer(QWidget):
    def __init__(self, mer: MerCalc):
        super().__init__()

        self.width = 950
        self.height = 400

        self.drawGridMer = DrawGridSolution(mer, self.width, self.height)

        self.initUI()

    def initUI(self):
        self.setMinimumSize(self.width, self.height)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawGridMer.drawGS(qp)
        qp.end()


from PyQt5.QtWidgets import QApplication
import sys
if __name__ == "__main__":
    mer = test()
    string = merSoltoText(mer)
    print(string)
    app = QApplication(sys.argv)
    ex = GridMer(mer)
    ex.show()
    sys.exit(app.exec())
