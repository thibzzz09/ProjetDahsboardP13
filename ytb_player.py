import subprocess
import sys
from threading import Thread
from math import sqrt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pytube


class YoutubePlayer(QMainWindow):
    def __init__(self):
        super(YoutubePlayer, self).__init__()

        self.url = "https://www.youtube.com/watch?v=ekOPUNwXMlg"
        self.urlId = self.url.split('v=')[-1]

        self.defaultResolutions = {
            "hd1440": "2560 x 1440",
            "hd1080": "1920 x 1080",
            "720": "1280 x 720",
            "480": "854 x 480",
            "360": "640 x 360",
            "240": "426 x 240"
        }

        ###################################################################################

        self.setWindowTitle('Dashboard LA/P13 - Victor-Alexis PACAUD / Thibault RICHEL')
        self.setMinimumSize(1200, 600)

        self.centralWidget = QWidget()
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        # --------------------------------------------------------------------------------- QWebView

        # results = self.getBestQualityCodecFramerate()
        self.bestQuality, self.codec, self.framerate = self.getBestQualityCodecFramerate()
        if int(self.bestQuality) > 720:
            self.bestQuality = 'hd' + str(self.bestQuality)
        self.webView = QWebEngineView()

        htmlString = f"""
                    <iframe 
                            src="https://www.youtube.com/embed/{self.urlId}?autoplay=0&showinfo=0&
                            vq={self.bestQuality}&controls=0"
                            width="100%" height="100%" 
                            frameborder="0" allowautoplay>
                    </iframe>
                     """
        self.webView.setHtml(htmlString, QUrl(self.url))

        # --------------------------------------------------------------------------------- Stats

        # Stylesheets
        title = "QLabel { font: 30px; text-decoration: underline; font-weight: bold }"
        subtitle = "QLabel { font: 18px; text-decoration: underline }"
        gridLabel = "QLabel { font: 14px }"
        gridValue = "QLabel { font: 14px; font-weight: bold }"

        # Main widgets and layouts
        self.statsWidget = QWidget()
        self.statsWidget.setMinimumWidth(200)
        self.statsWidget.setMaximumWidth(round(self.width() * 25 / 100))
        self.statsLayout = QVBoxLayout()
        self.statsWidget.setLayout(self.statsLayout)

        self.title = QLabel("Statistics")
        self.title.setMaximumHeight(50)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(title)

        # Network stats
        self.networkStatsLabel = QLabel("Network informations :")
        self.networkStatsLabel.setMaximumHeight(40)
        self.networkStatsLabel.setStyleSheet(subtitle)

        self.networkContentWidget = QWidget()
        self.networkContentLayout = QGridLayout()
        self.networkContentWidget.setLayout(self.networkContentLayout)

        self.latencyLabel = QLabel("Latency :")
        self.latencyLabel.setStyleSheet(gridLabel)

        self.latencyValue = QLabel("Click on 'Start measuring'")
        self.latencyValue.setStyleSheet(gridValue)

        self.jitterLabel = QLabel("Jitter :")
        self.jitterLabel.setStyleSheet(gridLabel)

        self.jitterValue = QLabel("Click on 'Start measuring'")
        self.jitterValue.setStyleSheet(gridValue)

        self.packetLossLabel = QLabel("Packet Loss :")
        self.packetLossLabel.setStyleSheet(gridLabel)

        self.packetLossValue = QLabel("Click on 'Start measuring'")
        self.packetLossValue.setStyleSheet(gridValue)

        self.bandwidthLabel = QLabel("Bandwidth (up/down) :")
        self.bandwidthLabel.setStyleSheet(gridLabel)

        self.bandwidthValue = QLabel("Click on 'Start measuring'")
        self.bandwidthValue.setStyleSheet(gridValue)

        self.networkContentLayout.addWidget(self.latencyLabel, 0, 0)
        self.networkContentLayout.addWidget(self.latencyValue, 0, 1)
        self.networkContentLayout.addWidget(self.jitterLabel, 1, 0)
        self.networkContentLayout.addWidget(self.jitterValue, 1, 1)
        self.networkContentLayout.addWidget(self.packetLossLabel, 2, 0)
        self.networkContentLayout.addWidget(self.packetLossValue, 2, 1)
        self.networkContentLayout.addWidget(self.bandwidthLabel, 3, 0)
        self.networkContentLayout.addWidget(self.bandwidthValue, 3, 1)

        # Video stats
        self.videoStatsLabel = QLabel("Video informations :")
        self.videoStatsLabel.setMaximumHeight(40)
        self.videoStatsLabel.setStyleSheet(subtitle)

        self.videoContentWidget = QWidget()
        self.videoContentLayout = QGridLayout()
        self.videoContentWidget.setLayout(self.videoContentLayout)

        self.codecLabel = QLabel("Codec :")
        self.codecLabel.setStyleSheet(gridLabel)

        self.codecValue = QLabel("Click on 'Start measuring'")
        self.codecValue.setStyleSheet(gridValue)

        self.resolutionLabel = QLabel("Resolution :")
        self.resolutionLabel.setStyleSheet(gridLabel)

        self.resolutionValue = QLabel("Click on 'Start measuring'")
        self.resolutionValue.setStyleSheet(gridValue)

        self.framerateLabel = QLabel("Frame rate :")
        self.framerateLabel.setStyleSheet(gridLabel)

        self.framerateValue = QLabel("Click on 'Start measuring'")
        self.framerateValue.setStyleSheet(gridValue)

        self.videoContentLayout.addWidget(self.codecLabel, 0, 0)
        self.videoContentLayout.addWidget(self.codecValue, 0, 1)
        self.videoContentLayout.addWidget(self.resolutionLabel, 1, 0)
        self.videoContentLayout.addWidget(self.resolutionValue, 1, 1)
        self.videoContentLayout.addWidget(self.framerateLabel, 2, 0)
        self.videoContentLayout.addWidget(self.framerateValue, 2, 1)

        self.btnStartMeasuring = QPushButton("Start measuring")
        self.btnStartMeasuring.clicked.connect(self.startThreads)

        # Adding widgets
        self.statsLayout.addWidget(self.title)
        self.statsLayout.addWidget(self.networkStatsLabel)
        self.statsLayout.addWidget(self.networkContentWidget)
        self.statsLayout.addWidget(self.videoStatsLabel)
        self.statsLayout.addWidget(self.videoContentWidget)
        self.statsLayout.addWidget(self.btnStartMeasuring)

        ###################################################################################

        self.mainLayout.addWidget(self.webView)
        self.mainLayout.addWidget(self.statsWidget)
        self.showMaximized()

    def resizeEvent(self, event):
        self.statsWidget.setMaximumWidth(round(self.width() * 25 / 100))

    def startThreads(self):
        self.latencyValue.setText('collecting...')
        self.packetLossValue.setText('collecting...')
        self.jitterValue.setText('collecting...')
        self.bandwidthValue.setText('collecting...')
        self.resolutionValue.setText(self.defaultResolutions[self.bestQuality])
        self.codecValue.setText(self.codec)
        self.framerateValue.setText(f'{str(self.framerate)} fps')
        thread1 = Thread(target=self.displayAllStats)
        thread1.start()

    def displayAllStats(self):
        latency, jitter, packetloss, upVal, upUnit, downVal, downUnit = self.getAllStats()
        self.latencyValue.setText(f"{latency} ms")
        self.jitterValue.setText(f"{jitter} ms")
        self.packetLossValue.setText(f"{packetloss} %")
        self.bandwidthValue.setText(f"{upVal} {upUnit}  /  {downVal} {downUnit}")

    def getAllStats(self):
        lats = []
        res = subprocess.check_output(f"serviceping {self.url} -c 5", shell=True).decode('utf-8')
        lines = res.split('\n')
        packetloss = 'unknown'

        for li in lines:
            if 'time=' in li:
                lat = float(li.split('time=')[-1].split(' ')[0])
                lats.append(lat)
            if 'packet loss' in li:
                packetloss = float(li.split(', ')[2].split('%')[0])

        summ = jit = 0
        for la in lats:
            summ += la
        mean = summ/len(lats)
        jitters = [(mean - lat)**2 for lat in lats]
        for j in jitters:
            jit += j
        jitter = round(sqrt(jit/len(jitters)), 2)
        latency = round(mean, 2)

        bw = subprocess.check_output("speedtest", shell=True).decode('utf-8')
        lines = bw.split('\n')
        upVal = downVal = downUnit = upUnit = 'unknown'
        for li in lines:
            if 'Download' in li:
                downVal = float(li.split(' ')[1])
                downUnit = li.split(' ')[-1]
            if 'Upload' in li:
                upVal = float(li.split(' ')[1])
                upUnit = li.split(' ')[-1]

        return latency, jitter, packetloss, upVal, upUnit, downVal, downUnit

    def getBestQualityCodecFramerate(self):
        vid = pytube.YouTube(self.url)
        streams = [stream for stream in vid.streams if not stream.is_progressive]
        results = []
        for i, s in enumerate(streams):
            if s.resolution is not None:
                resol = int(s.resolution.replace('p', ''))
                codec = vid.streams[i].video_codec.split('.')[0]
                rate = vid.streams[i].fps
                results.append((resol, codec, rate))
        final = max(results, key=lambda x: x[0])
        return final


if __name__ == '__main__':
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = YoutubePlayer()
    window.show()
    app.exec_()
