import sys
import gpxpy
import math
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

class GPXViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yarış Haritası")
        self.setGeometry(100, 100, 800, 600)

        # Arka plan
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.tur_sayisi = 0
        self.label = QLabel("Tur Sayısı: 0")
        self.label.setStyleSheet("color: white; font-size: 20px;")
        self.label.setAlignment(Qt.AlignLeft)

        self.plot_button = QPushButton("Haritayı Göster")
        self.plot_button.clicked.connect(self.plot_gpx)

        self.figure = Figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.plot_button)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)
        a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def plot_gpx(self):
        with open("track.gpx", "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        lats, lons = [], []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lats.append(point.latitude)
                    lons.append(point.longitude)

        if not lats or not lons:
            self.label.setText("GPX verisi bulunamadı.")
            return

        baslangic_lat = lats[0]
        baslangic_lon = lons[0]

        # Tur sayımı
        self.tur_sayisi = 0
        threshold = 5
        min_ayrilma_mesafesi = 15
        ayrildi = False

        for i in range(1, len(lats)):
            mesafe = self.haversine(lats[i], lons[i], baslangic_lat, baslangic_lon)
            if mesafe > min_ayrilma_mesafesi:
                ayrildi = True
            if mesafe < threshold and ayrildi:
                self.tur_sayisi += 1
                ayrildi = False

        self.label.setText(f"Tur Sayısı: {self.tur_sayisi}")

        # Haritayı çiz
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('black')
        ax.plot(lons, lats, color='white', linewidth=6)

        # Başlangıç noktasına bayrak ekle
        try:
            image = mpimg.imread("flag.png")  # 📌 PNG bayrak ikonunu aynı klasöre koy!
            imagebox = OffsetImage(image, zoom=0.05)
            ab = AnnotationBbox(imagebox, (baslangic_lon, baslangic_lat), frameon=False)
            ax.add_artist(ab)
        except Exception as e:
            print("Bayrak yüklenemedi:", e)

        ax.axis('off')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = GPXViewer()
    viewer.show()
    sys.exit(app.exec_())
