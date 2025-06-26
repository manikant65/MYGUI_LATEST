'''import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QLabel, QTabWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6 import QtCore
from queue import Queue, Empty
import pyqtgraph as pg
import time

class MainWindow(QWidget):
    def __init__(self, data_queue, processor):
        super().__init__()
        self.setObjectName("mainWindow")
        self.data_queue = data_queue
        self.processor = processor
        self.start_time = time.time()  # Track start time for moving line graphs
        self.init_ui()
        self.setup_plots()
        self.setup_timer()
        self.setup_marquee()

    def init_ui(self):
        self.setWindowTitle("QUANTUM KEY DISTRIBUTION")
        self.resize(1000, 700)  # Default window size
        self.setMinimumSize(1000, 700)  # Prevent resizing too small

        # Apply stylesheet with vibrant color scheme
        self.setStyleSheet("""
            QWidget#mainWindow {
                background-color: #006064;  /* Deep teal for main window */
                color: #F0F4F5;  /* Off-white text */
                font-family: Arial;
            }
            QTabWidget::pane {
                background-color: #006064;  /* Deep teal for tab content area */
                border: 1px solid #B0BEC5;  /* Subtle gray border */
            }
            QTabBar::tab {
                background-color: #37474F;  /* Dark slate for tabs */
                color: #B2EBF2;  /* Light cyan text */
                padding: 8px 20px;
                font-size: 12pt;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab:selected {
                background-color: #26A69A;  /* Soft teal for selected tab */
                color: #F0F4F5;  /* Off-white text */
            }
            QPushButton {
                background-color: #26A69A;  /* Bright green for Start */
                color: #F0F4F5;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#stopButton {
                background-color: #EF5350;  /* Warm red for Stop */
            }
            QPushButton:hover {
                background-color: #2BBBAD;  /* Lighter green on hover */
            }
            QPushButton#stopButton:hover {
                background-color: #E53935;  /* Darker red on hover */
            }
            pg.PlotWidget {
                border: 1px solid #B0BEC5;  /* Subtle gray border */
                background-color: #D1C4E9;  /* Soft lavender for all plots */
            }
            QLabel#marqueeLabel {
                color: #B2EBF2;  /* Light cyan text */
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
            QLabel#keyDisplay {
                color: #F0F4F5;  /* Off-white text */
                font-family: Consolas;
                font-size: 12px;
                padding: 5px;
                text-align: center;
            }
            QWidget#marqueeContainer, QWidget#buttonContainer, QWidget#keyContainer {
                background-color: #37474F;  /* Dark slate for containers */
                border: 1px solid #B0BEC5;  /* Subtle gray border */
                padding: 5px;
            }
            QWidget#marqueeContainer, QWidget#keyContainer {
                max-height: 60px;  /* Thin containers */
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()

        # Marquee container at top
        marquee_container = QWidget(objectName="marqueeContainer")
        marquee_layout = QHBoxLayout()
        marquee_layout.addStretch()
        self.marquee_label = QLabel("Welcome To Quantum Key Distribution Output Analyzer   ", objectName="marqueeLabel")
        marquee_layout.addWidget(self.marquee_label)
        marquee_layout.addStretch()
        marquee_container.setLayout(marquee_layout)
        main_layout.addWidget(marquee_container)

        # Tab widget
        tab_widget = QTabWidget()

        # --- All Tab (two histograms side by side, QBER, kbps, visibility, spd1) ---
        all_tab = QWidget()
        all_layout = QVBoxLayout()

        # Histogram container in All tab (two histograms side by side)
        hist_container_all = QHBoxLayout()
        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        # First Histogram in All tab
        self.hist_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_container_all.addWidget(self.hist_plot_all)

        # Second Histogram in All tab
        self.hist2_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist_container_all.addWidget(self.hist2_plot_all)

        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        all_layout.addLayout(hist_container_all)
        all_layout.setStretchFactor(hist_container_all, 3)

        # Bottom grid in All tab (QBER, kbps, visibility, spd1)
        bottom_layout_all = QGridLayout()
        bottom_layout_all.setSpacing(10)

        self.qber_plot_all = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        bottom_layout_all.addWidget(self.qber_plot_all, 0, 0)

        self.kbps_plot_all = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        bottom_layout_all.addWidget(self.kbps_plot_all, 0, 1)

        self.visibility_plot_all = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        bottom_layout_all.addWidget(self.visibility_plot_all, 1, 0)

        self.spd1_plot_all = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        bottom_layout_all.addWidget(self.spd1_plot_all, 1, 1)

        all_layout.addLayout(bottom_layout_all)
        all_layout.setStretchFactor(bottom_layout_all, 2)

        all_tab.setLayout(all_layout)
        tab_widget.addTab(all_tab, "All")

        # --- Dedicated Tabs (Histogram (SPD1), Histogram (SPD2), QBER, kbps, visibility, spd1) ---

        # Histogram (SPD1) Tab
        hist_tab = QWidget()
        hist_tab_layout = QHBoxLayout()
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_tab_layout.addWidget(self.hist_plot_tab)
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist_tab.setLayout(hist_tab_layout)
        tab_widget.addTab(hist_tab, "Histogram (SPD1)")

        # Histogram (SPD2) Tab
        hist2_tab = QWidget()
        hist2_tab_layout = QHBoxLayout()
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist2_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist2_tab_layout.addWidget(self.hist2_plot_tab)
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist2_tab.setLayout(hist2_tab_layout)
        tab_widget.addTab(hist2_tab, "Histogram (SPD2)")

        # QBER Tab
        qber_tab = QWidget()
        qber_tab_layout = QHBoxLayout()
        qber_tab_layout.addStretch()
        self.qber_plot_tab = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        self.qber_plot_tab.setFixedSize(600, 400)
        qber_tab_layout.addWidget(self.qber_plot_tab)
        qber_tab_layout.addStretch()
        qber_tab.setLayout(qber_tab_layout)
        tab_widget.addTab(qber_tab, "QBER")

        # kbps Tab
        kbps_tab = QWidget()
        kbps_tab_layout = QHBoxLayout()
        kbps_tab_layout.addStretch()
        self.kbps_plot_tab = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        self.kbps_plot_tab.setFixedSize(600, 400)
        kbps_tab_layout.addWidget(self.kbps_plot_tab)
        kbps_tab_layout.addStretch()
        kbps_tab.setLayout(kbps_tab_layout)
        tab_widget.addTab(kbps_tab, "Throughput")

        # Visibility Tab
        visibility_tab = QWidget()
        visibility_tab_layout = QHBoxLayout()
        visibility_tab_layout.addStretch()
        self.visibility_plot_tab = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        self.visibility_plot_tab.setFixedSize(600, 400)
        visibility_tab_layout.addWidget(self.visibility_plot_tab)
        visibility_tab_layout.addStretch()
        visibility_tab.setLayout(visibility_tab_layout)
        tab_widget.addTab(visibility_tab, "Visibility")

        # SPD1 DecoyState Tab
        spd1_tab = QWidget()
        spd1_tab_layout = QHBoxLayout()
        spd1_tab_layout.addStretch()
        self.spd1_plot_tab = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        self.spd1_plot_tab.setFixedSize(600, 400)
        spd1_tab_layout.addWidget(self.spd1_plot_tab)
        spd1_tab_layout.addStretch()
        spd1_tab.setLayout(spd1_tab_layout)
        tab_widget.addTab(spd1_tab, "SPD1 Decoy Randomness")

        main_layout.addWidget(tab_widget)

        # Key container above button container
        key_container = QWidget(objectName="keyContainer")
        key_layout = QHBoxLayout()
        key_layout.addStretch()
        self.key_display = QLabel("Key: None", objectName="keyDisplay")
        key_layout.addWidget(self.key_display)
        key_layout.addStretch()
        key_container.setLayout(key_layout)
        main_layout.addWidget(key_container)

        # Button container at bottom
        button_container = QWidget(objectName="buttonContainer")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.start_button.clicked.connect(self.start_processor)
        self.stop_button.clicked.connect(self.stop_processor)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def setup_marquee(self):
        self.marquee_timer = QTimer(self)
        self.marquee_timer.setInterval(150)
        self.marquee_timer.timeout.connect(self.update_marquee)
        self.marquee_timer.start()

    def update_marquee(self):
        text = self.marquee_label.text()
        text = text[1:] + text[0]
        self.marquee_label.setText(text)

    def setup_plots(self):
        pg.setConfigOptions(antialias=True)

        # Helper function for line plot configuration
        def configure_line_plot(plot_widget, y_label, title, x_range=(0, 60000), y_range=(0, 10)):
            plot_widget.setLabel('bottom', 'Time (ms)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', y_label, color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)
            plot_widget.setYRange(*y_range)

        def configure_histogram_plot(plot_widget, title, brush_color, x_range=(0, 4000)):
            plot_widget.setLabel('bottom', 'Time (ps)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', 'Count', color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)

        # --- Histogram (SPD1) setup for 'All' tab ---
        self.hist_data_all = np.zeros(40)
        self.hist_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_all, width=100, brush='#FF6F61')
        self.hist_plot_all.addItem(self.hist_bar_all)
        configure_histogram_plot(self.hist_plot_all, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_all = []
        bar_centers = np.arange(40)*100 + 50
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_all[i] + 0.5)
            self.hist_plot_all.addItem(label)
            self.hist_labels_all.append(label)

        # --- Histogram (SPD2) setup for 'All' tab ---
        self.hist2_data_all = np.zeros(40)
        self.hist2_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_all, width=100, brush='#FFCA28')
        self.hist2_plot_all.addItem(self.hist2_bar_all)
        configure_histogram_plot(self.hist2_plot_all, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_all = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_all[i] + 0.5)
            self.hist2_plot_all.addItem(label)
            self.hist2_labels_all.append(label)

        # --- Histogram (SPD1) setup for 'Histogram (SPD1)' tab ---
        self.hist_data_tab = np.zeros(40)
        self.hist_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_tab, width=100, brush='#FF6F61')
        self.hist_plot_tab.addItem(self.hist_bar_tab)
        configure_histogram_plot(self.hist_plot_tab, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_tab[i] + 0.5)
            self.hist_plot_tab.addItem(label)
            self.hist_labels_tab.append(label)

        # --- Histogram (SPD2) setup for 'Histogram (SPD2)' tab ---
        self.hist2_data_tab = np.zeros(40)
        self.hist2_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_tab, width=100, brush='#FFCA28')
        self.hist2_plot_tab.addItem(self.hist2_bar_tab)
        configure_histogram_plot(self.hist2_plot_tab, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_tab[i] + 0.5)
            self.hist2_plot_tab.addItem(label)
            self.hist2_labels_tab.append(label)

        # --- QBER plots (Moving Line Graph) ---
        self.qber_x_all = []
        self.qber_y_all = []
        self.qber_line_all = self.qber_plot_all.plot(self.qber_x_all, self.qber_y_all, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_all, 'QBER (%)', "Quantum Bit Error Rate")

        self.qber_x_tab = []
        self.qber_y_tab = []
        self.qber_line_tab = self.qber_plot_tab.plot(self.qber_x_tab, self.qber_y_tab, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_tab, 'QBER (%)', "Quantum Bit Error Rate")

        # --- Throughput (kbps) plots (Moving Line Graph) ---
        self.kbps_x_all = []
        self.kbps_y_all = []
        self.kbps_line_all = self.kbps_plot_all.plot(self.kbps_x_all, self.kbps_y_all, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_all, 'kbps', "Throughput (kbps)")

        self.kbps_x_tab = []
        self.kbps_y_tab = []
        self.kbps_line_tab = self.kbps_plot_tab.plot(self.kbps_x_tab, self.kbps_y_tab, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_tab, 'kbps', "Throughput (kbps)")

        # --- Visibility plots (Moving Line Graph) ---
        self.visibility_x_all = []
        self.visibility_y_all = []
        self.visibility_line_all = self.visibility_plot_all.plot(self.visibility_x_all, self.visibility_y_all, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_all, 'Ratio', "Visibility Ratio")

        self.visibility_x_tab = []
        self.visibility_y_tab = []
        self.visibility_line_tab = self.visibility_plot_tab.plot(self.visibility_x_tab, self.visibility_y_tab, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_tab, 'Ratio', "Visibility Ratio")

        # --- SPD1 Decoy Randomness plots (Moving Line Graph) ---
        self.spd1_x_all = []
        self.spd1_y_all = []
        self.spd1_line_all = self.spd1_plot_all.plot(self.spd1_x_all, self.spd1_y_all, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_all, 'Value', "SPD1 Decoy Randomness")

        self.spd1_x_tab = []
        self.spd1_y_tab = []
        self.spd1_line_tab = self.spd1_plot_tab.plot(self.spd1_x_tab, self.spd1_y_tab, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_tab, 'Value', "SPD1 Decoy Randomness")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1)  # Update every 1ms to match data rate
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

    def update_plots(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                current_time = (time.time() - self.start_time) * 1000  # Time in milliseconds

                if data['type'] == 'timestamp_spd1':
                    timestamp_ps = int(data['value'])
                    partition1 = min((timestamp_ps // 100) % 40, 39)
                    self.hist_data_all[partition1] += 1
                    self.hist_bar_all.setOpts(height=self.hist_data_all)
                    self.hist_labels_all[partition1].setText(str(int(self.hist_data_all[partition1])))
                    self.hist_labels_all[partition1].setPos(partition1*100 + 50, self.hist_data_all[partition1] + 0.5)
                    self.hist_plot_all.setYRange(0, max(self.hist_data_all.max() * 1.1, 10))

                    self.hist_data_tab[partition1] += 1
                    self.hist_bar_tab.setOpts(height=self.hist_data_tab)
                    self.hist_labels_tab[partition1].setText(str(int(self.hist_data_tab[partition1])))
                    self.hist_labels_tab[partition1].setPos(partition1*100 + 50, self.hist_data_tab[partition1] + 0.5)
                    self.hist_plot_tab.setYRange(0, max(self.hist_data_tab.max() * 1.1, 10))

                elif data['type'] == 'timestamp_spd2':
                    timestamp_ps = int(data['value'])
                    partition2 = min((timestamp_ps // 100) % 40, 39)
                    self.hist2_data_all[partition2] += 1
                    self.hist2_bar_all.setOpts(height=self.hist2_data_all)
                    self.hist2_labels_all[partition2].setText(str(int(self.hist2_data_all[partition2])))
                    self.hist2_labels_all[partition2].setPos(partition2*100 + 50, self.hist2_data_all[partition2] + 0.5)
                    self.hist2_plot_all.setYRange(0, max(self.hist2_data_all.max() * 1.1, 10))

                    self.hist2_data_tab[partition2] += 1
                    self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
                    self.hist2_labels_tab[partition2].setText(str(int(self.hist2_data_tab[partition2])))
                    self.hist2_labels_tab[partition2].setPos(partition2*100 + 50, self.hist2_data_tab[partition2] + 0.5)
                    self.hist2_plot_tab.setYRange(0, max(self.hist2_data_tab.max() * 1.1, 10))

                elif data['type'] == 'qber':
                    qber_val = float(data['value'])
                    self.qber_x_all.append(current_time)
                    self.qber_y_all.append(qber_val)
                    while self.qber_x_all and self.qber_x_all[0] < current_time - 60000:  # Last 60 seconds in ms
                        self.qber_x_all.pop(0)
                        self.qber_y_all.pop(0)
                    self.qber_line_all.setData(self.qber_x_all, self.qber_y_all)
                    self.qber_plot_all.setXRange(max(0, current_time - 60000), current_time)

                    self.qber_x_tab.append(current_time)
                    self.qber_y_tab.append(qber_val)
                    while self.qber_x_tab and self.qber_x_tab[0] < current_time - 60000:
                        self.qber_x_tab.pop(0)
                        self.qber_y_tab.pop(0)
                    self.qber_line_tab.setData(self.qber_x_tab, self.qber_y_tab)
                    self.qber_plot_tab.setXRange(max(0, current_time - 60000), current_time)

                elif data['type'] == 'kbps_data':
                    kbps = float(data['kbps'])
                    self.kbps_x_all.append(current_time)
                    self.kbps_y_all.append(kbps)
                    while self.kbps_x_all and self.kbps_x_all[0] < current_time - 60000:
                        self.kbps_x_all.pop(0)
                        self.kbps_y_all.pop(0)
                    self.kbps_line_all.setData(self.kbps_x_all, self.kbps_y_all)
                    self.kbps_plot_all.setXRange(max(0, current_time - 60000), current_time)

                    self.kbps_x_tab.append(current_time)
                    self.kbps_y_tab.append(kbps)
                    while self.kbps_x_tab and self.kbps_x_tab[0] < current_time - 60000:
                        self.kbps_x_tab.pop(0)
                        self.kbps_y_tab.pop(0)
                    self.kbps_line_tab.setData(self.kbps_x_tab, self.kbps_y_tab)
                    self.kbps_plot_tab.setXRange(max(0, current_time - 60000), current_time)

                elif data['type'] == 'key':
                    self.key_display.setText(str(data['value']))

                elif data['type'] == 'visibility':
                    vis_val = float(data['value'])
                    self.visibility_x_all.append(current_time)
                    self.visibility_y_all.append(vis_val)
                    while self.visibility_x_all and self.visibility_x_all[0] < current_time - 60000:
                        self.visibility_x_all.pop(0)
                        self.visibility_y_all.pop(0)
                    self.visibility_line_all.setData(self.visibility_x_all, self.visibility_y_all)
                    self.visibility_plot_all.setXRange(max(0, current_time - 60000), current_time)

                    self.visibility_x_tab.append(current_time)
                    self.visibility_y_tab.append(vis_val)
                    while self.visibility_x_tab and self.visibility_x_tab[0] < current_time - 60000:
                        self.visibility_x_tab.pop(0)
                        self.visibility_y_tab.pop(0)
                    self.visibility_line_tab.setData(self.visibility_x_tab, self.visibility_y_tab)
                    self.visibility_plot_tab.setXRange(max(0, current_time - 60000), current_time)

                elif data['type'] == 'spd1_decaystate':
                    spd1_val = float(data['value'])
                    self.spd1_x_all.append(current_time)
                    self.spd1_y_all.append(spd1_val)
                    while self.spd1_x_all and self.spd1_x_all[0] < current_time - 60000:
                        self.spd1_x_all.pop(0)
                        self.spd1_y_all.pop(0)
                    self.spd1_line_all.setData(self.spd1_x_all, self.spd1_y_all)
                    self.spd1_plot_all.setXRange(max(0, current_time - 60000), current_time)

                    self.spd1_x_tab.append(current_time)
                    self.spd1_y_tab.append(spd1_val)
                    while self.spd1_x_tab and self.spd1_x_tab[0] < current_time - 60000:
                        self.spd1_x_tab.pop(0)
                        self.spd1_y_tab.pop(0)
                    self.spd1_line_tab.setData(self.spd1_x_tab, self.spd1_y_tab)
                    self.spd1_plot_tab.setXRange(max(0, current_time - 60000), current_time)

        except Empty:
            pass

    def start_processor(self):
        self.processor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_processor(self):
        self.processor.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


    def closeEvent(self, event):
        self.processor.close()
        self.marquee_timer.stop()
        event.accept()'''
        

'''
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QLabel, QTabWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6 import QtCore
from queue import Queue, Empty
import pyqtgraph as pg
import time

class MainWindow(QWidget):
    def __init__(self, data_queue, processor):
        super().__init__()
        self.setObjectName("mainWindow")
        self.data_queue = data_queue
        self.processor = processor
        self.start_time = time.time()  # Track start time for moving line graphs
        self.init_ui()
        self.setup_plots()
        self.setup_timer()
        self.setup_marquee()

    def init_ui(self):
        self.setWindowTitle("QUANTUM KEY DISTRIBUTION")
        self.resize(1000, 700)  # Default window size
        self.setMinimumSize(1000, 700)  # Prevent resizing too small

        # Apply stylesheet with vibrant color scheme
        self.setStyleSheet("""
            QWidget#mainWindow {
                background-color: #006064;  /* Deep teal for main window */
                color: #F0F4F5;  /* Off-white text */
                font-family: Arial;
            }
            QTabWidget::pane {
                background-color: #006064;  /* Deep teal for tab content area */
                border: 1px solid #B0BEC5;  /* Subtle gray border */
            }
            QTabBar::tab {
                background-color: #37474F;  /* Dark slate for tabs */
                color: #B2EBF2;  /* Light cyan text */
                padding: 8px 20px;
                font-size: 12pt;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab:selected {
                background-color: #26A69A;  /* Soft teal for selected tab */
                color: #F0F4F5;  /* Off-white text */
            }
            QPushButton {
                background-color: #26A69A;  /* Bright green for Start */
                color: #F0F4F5;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#stopButton {
                background-color: #EF5350;  /* Warm red for Stop */
            }
            QPushButton:hover {
                background-color: #2BBBAD;  /* Lighter green on hover */
            }
            QPushButton#stopButton:hover {
                background-color: #E53935;  /* Darker red on hover */
            }
            pg.PlotWidget {
                border: 1px solid #B0BEC5;  /* Subtle gray border */
                background-color: #D1C4E9;  /* Soft lavender for all plots */
            }
            QLabel#marqueeLabel {
                color: #B2EBF2;  /* Light cyan text */
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
            QLabel#keyDisplay {
                color: #F0F4F5;  /* Off-white text */
                font-family: Consolas;
                font-size: 12px;
                padding: 5px;
                text-align: center;
            }
            QWidget#marqueeContainer, QWidget#buttonContainer, QWidget#keyContainer {
                background-color: #37474F;  /* Dark slate for containers */
                border: 1px solid #B0BEC5;  /* Subtle gray border */
                padding: 5px;
            }
            QWidget#marqueeContainer, QWidget#keyContainer {
                max-height: 60px;  /* Thin containers */
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()

        # Marquee container at top
        marquee_container = QWidget(objectName="marqueeContainer")
        marquee_layout = QHBoxLayout()
        marquee_layout.addStretch()
        self.marquee_label = QLabel("Welcome To Quantum Key Distribution Output Analyzer   ", objectName="marqueeLabel")
        marquee_layout.addWidget(self.marquee_label)
        marquee_layout.addStretch()
        marquee_container.setLayout(marquee_layout)
        main_layout.addWidget(marquee_container)

        # Tab widget
        tab_widget = QTabWidget()

        # --- All Tab (two histograms side by side, QBER, kbps, visibility, spd1) ---
        all_tab = QWidget()
        all_layout = QVBoxLayout()

        # Histogram container in All tab (two histograms side by side)
        hist_container_all = QHBoxLayout()
        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        # First Histogram in All tab
        self.hist_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_container_all.addWidget(self.hist_plot_all)

        # Second Histogram in All tab
        self.hist2_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist_container_all.addWidget(self.hist2_plot_all)

        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        all_layout.addLayout(hist_container_all)
        all_layout.setStretchFactor(hist_container_all, 3)

        # Bottom grid in All tab (QBER, kbps, visibility, spd1)
        bottom_layout_all = QGridLayout()
        bottom_layout_all.setSpacing(10)

        self.qber_plot_all = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        bottom_layout_all.addWidget(self.qber_plot_all, 0, 0)

        self.kbps_plot_all = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        bottom_layout_all.addWidget(self.kbps_plot_all, 0, 1)

        self.visibility_plot_all = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        bottom_layout_all.addWidget(self.visibility_plot_all, 1, 0)

        self.spd1_plot_all = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        bottom_layout_all.addWidget(self.spd1_plot_all, 1, 1)

        all_layout.addLayout(bottom_layout_all)
        all_layout.setStretchFactor(bottom_layout_all, 2)

        all_tab.setLayout(all_layout)
        tab_widget.addTab(all_tab, "All")

        # --- Dedicated Tabs (Histogram (SPD1), Histogram (SPD2), QBER, kbps, visibility, spd1) ---

        # Histogram (SPD1) Tab
        hist_tab = QWidget()
        hist_tab_layout = QHBoxLayout()
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_tab_layout.addWidget(self.hist_plot_tab)
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist_tab.setLayout(hist_tab_layout)
        tab_widget.addTab(hist_tab, "Histogram (SPD1)")

        # Histogram (SPD2) Tab
        hist2_tab = QWidget()
        hist2_tab_layout = QHBoxLayout()
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist2_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist2_tab_layout.addWidget(self.hist2_plot_tab)
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist2_tab.setLayout(hist2_tab_layout)
        tab_widget.addTab(hist2_tab, "Histogram (SPD2)")

        # QBER Tab
        qber_tab = QWidget()
        qber_tab_layout = QHBoxLayout()
        qber_tab_layout.addStretch()
        self.qber_plot_tab = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        self.qber_plot_tab.setFixedSize(600, 400)
        qber_tab_layout.addWidget(self.qber_plot_tab)
        qber_tab_layout.addStretch()
        qber_tab.setLayout(qber_tab_layout)
        tab_widget.addTab(qber_tab, "QBER")

        # kbps Tab
        kbps_tab = QWidget()
        kbps_tab_layout = QHBoxLayout()
        kbps_tab_layout.addStretch()
        self.kbps_plot_tab = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        self.kbps_plot_tab.setFixedSize(600, 400)
        kbps_tab_layout.addWidget(self.kbps_plot_tab)
        kbps_tab_layout.addStretch()
        kbps_tab.setLayout(kbps_tab_layout)
        tab_widget.addTab(kbps_tab, "Throughput")

        # Visibility Tab
        visibility_tab = QWidget()
        visibility_tab_layout = QHBoxLayout()
        visibility_tab_layout.addStretch()
        self.visibility_plot_tab = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        self.visibility_plot_tab.setFixedSize(600, 400)
        visibility_tab_layout.addWidget(self.visibility_plot_tab)
        visibility_tab_layout.addStretch()
        visibility_tab.setLayout(visibility_tab_layout)
        tab_widget.addTab(visibility_tab, "Visibility")

        # SPD1 DecoyState Tab
        spd1_tab = QWidget()
        spd1_tab_layout = QHBoxLayout()
        spd1_tab_layout.addStretch()
        self.spd1_plot_tab = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        self.spd1_plot_tab.setFixedSize(600, 400)
        spd1_tab_layout.addWidget(self.spd1_plot_tab)
        spd1_tab_layout.addStretch()
        spd1_tab.setLayout(spd1_tab_layout)
        tab_widget.addTab(spd1_tab, "SPD1 Decoy Randomness")

        main_layout.addWidget(tab_widget)

        # Key container above button container
        key_container = QWidget(objectName="keyContainer")
        key_layout = QHBoxLayout()
        key_layout.addStretch()
        self.key_display = QLabel("Key: None", objectName="keyDisplay")
        key_layout.addWidget(self.key_display)
        key_layout.addStretch()
        key_container.setLayout(key_layout)
        main_layout.addWidget(key_container)

        # Button container at bottom
        button_container = QWidget(objectName="buttonContainer")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.start_button.clicked.connect(self.start_processor)
        self.stop_button.clicked.connect(self.stop_processor)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def setup_marquee(self):
        self.marquee_timer = QTimer(self)
        self.marquee_timer.setInterval(150)
        self.marquee_timer.timeout.connect(self.update_marquee)
        self.marquee_timer.start()

    def update_marquee(self):
        text = self.marquee_label.text()
        text = text[1:] + text[0]
        self.marquee_label.setText(text)

    def setup_plots(self):
        pg.setConfigOptions(antialias=True)

        # Helper function for line plot configuration
        def configure_line_plot(plot_widget, y_label, title, x_range=(0, 60), y_range=(0, 10)): # x_range now in seconds (0 to 60)
            plot_widget.setLabel('bottom', 'Time (s)', color='#F0F4F5', size='12pt') # Changed to Time (s)
            plot_widget.setLabel('left', y_label, color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)
            plot_widget.setYRange(*y_range)

        def configure_histogram_plot(plot_widget, title, brush_color, x_range=(0, 4000)):
            plot_widget.setLabel('bottom', 'Time (ps)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', 'Count', color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)

        # --- Histogram (SPD1) setup for 'All' tab ---
        self.hist_data_all = np.zeros(40)
        self.hist_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_all, width=100, brush='#FF6F61')
        self.hist_plot_all.addItem(self.hist_bar_all)
        configure_histogram_plot(self.hist_plot_all, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_all = []
        bar_centers = np.arange(40)*100 + 50
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_all[i] + 0.5)
            self.hist_plot_all.addItem(label)
            self.hist_labels_all.append(label)

        # --- Histogram (SPD2) setup for 'All' tab ---
        self.hist2_data_all = np.zeros(40)
        self.hist2_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_all, width=100, brush='#FFCA28')
        self.hist2_plot_all.addItem(self.hist2_bar_all)
        configure_histogram_plot(self.hist2_plot_all, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_all = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_all[i] + 0.5)
            self.hist2_plot_all.addItem(label)
            self.hist2_labels_all.append(label)

        # --- Histogram (SPD1) setup for 'Histogram (SPD1)' tab ---
        self.hist_data_tab = np.zeros(40)
        self.hist_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_tab, width=100, brush='#FF6F61')
        self.hist_plot_tab.addItem(self.hist_bar_tab)
        configure_histogram_plot(self.hist_plot_tab, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_tab[i] + 0.5)
            self.hist_plot_tab.addItem(label)
            self.hist_labels_tab.append(label)

        # --- Histogram (SPD2) setup for 'Histogram (SPD2)' tab ---
        self.hist2_data_tab = np.zeros(40)
        self.hist2_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_tab, width=100, brush='#FFCA28')
        self.hist2_plot_tab.addItem(self.hist2_bar_tab)
        configure_histogram_plot(self.hist2_plot_tab, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_tab[i] + 0.5)
            self.hist2_plot_tab.addItem(label)
            self.hist2_labels_tab.append(label)

        # --- QBER plots (Moving Line Graph) ---
        self.qber_x_all = []
        self.qber_y_all = []
        self.qber_line_all = self.qber_plot_all.plot(self.qber_x_all, self.qber_y_all, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_all, 'QBER (%)', "Quantum Bit Error Rate")

        self.qber_x_tab = []
        self.qber_y_tab = []
        self.qber_line_tab = self.qber_plot_tab.plot(self.qber_x_tab, self.qber_y_tab, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_tab, 'QBER (%)', "Quantum Bit Error Rate")

        # --- Throughput (kbps) plots (Moving Line Graph) ---
        self.kbps_x_all = []
        self.kbps_y_all = []
        self.kbps_line_all = self.kbps_plot_all.plot(self.kbps_x_all, self.kbps_y_all, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_all, 'kbps', "Throughput (kbps)")

        self.kbps_x_tab = []
        self.kbps_y_tab = []
        self.kbps_line_tab = self.kbps_plot_tab.plot(self.kbps_x_tab, self.kbps_y_tab, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_tab, 'kbps', "Throughput (kbps)")

        # --- Visibility plots (Moving Line Graph) ---
        self.visibility_x_all = []
        self.visibility_y_all = []
        self.visibility_line_all = self.visibility_plot_all.plot(self.visibility_x_all, self.visibility_y_all, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_all, 'Ratio', "Visibility Ratio")

        self.visibility_x_tab = []
        self.visibility_y_tab = []
        self.visibility_line_tab = self.visibility_plot_tab.plot(self.visibility_x_tab, self.visibility_y_tab, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_tab, 'Ratio', "Visibility Ratio")

        # --- SPD1 Decoy Randomness plots (Moving Line Graph) ---
        self.spd1_x_all = []
        self.spd1_y_all = []
        self.spd1_line_all = self.spd1_plot_all.plot(self.spd1_x_all, self.spd1_y_all, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_all, 'Value', "SPD1 Decoy Randomness")

        self.spd1_x_tab = []
        self.spd1_y_tab = []
        self.spd1_line_tab = self.spd1_plot_tab.plot(self.spd1_x_tab, self.spd1_y_tab, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_tab, 'Value', "SPD1 Decoy Randomness")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1)  # Update every 1ms
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

    def update_plots(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                current_time = (time.time() - self.start_time) # Time in seconds

                if data['type'] == 'timestamp_spd1':
                    timestamp_ps = int(data['value'])
                    partition1 = min((timestamp_ps // 100) % 40, 39)
                    self.hist_data_all[partition1] += 1
                    self.hist_bar_all.setOpts(height=self.hist_data_all)
                    self.hist_labels_all[partition1].setText(str(int(self.hist_data_all[partition1])))
                    self.hist_labels_all[partition1].setPos(partition1*100 + 50, self.hist_data_all[partition1] + 0.5)
                    self.hist_plot_all.setYRange(0, max(self.hist_data_all.max() * 1.1, 10))

                    self.hist_data_tab[partition1] += 1
                    self.hist_bar_tab.setOpts(height=self.hist_data_tab)
                    self.hist_labels_tab[partition1].setText(str(int(self.hist_data_tab[partition1])))
                    self.hist_labels_tab[partition1].setPos(partition1*100 + 50, self.hist_data_tab[partition1] + 0.5)
                    self.hist_plot_tab.setYRange(0, max(self.hist_data_tab.max() * 1.1, 10))

                elif data['type'] == 'timestamp_spd2':
                    timestamp_ps = int(data['value'])
                    partition2 = min((timestamp_ps // 100) % 40, 39)
                    self.hist2_data_all[partition2] += 1
                    self.hist2_bar_all.setOpts(height=self.hist2_data_all)
                    self.hist2_labels_all[partition2].setText(str(int(self.hist2_data_all[partition2])))
                    self.hist2_labels_all[partition2].setPos(partition2*100 + 50, self.hist2_data_all[partition2] + 0.5)
                    self.hist2_plot_all.setYRange(0, max(self.hist2_data_all.max() * 1.1, 10))

                    self.hist2_data_tab[partition2] += 1
                    self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
                    self.hist2_labels_tab[partition2].setText(str(int(self.hist2_data_tab[partition2])))
                    self.hist2_labels_tab[partition2].setPos(partition2*100 + 50, self.hist2_data_tab[partition2] + 0.5)
                    self.hist2_plot_tab.setYRange(0, max(self.hist2_data_tab.max() * 1.1, 10))

                elif data['type'] == 'qber':
                    qber_val = float(data['value'])
                    self.qber_x_all.append(current_time)
                    self.qber_y_all.append(qber_val)
                    while self.qber_x_all and self.qber_x_all[0] < current_time - 60:  # Last 60 seconds
                        self.qber_x_all.pop(0)
                        self.qber_y_all.pop(0)
                    self.qber_line_all.setData(self.qber_x_all, self.qber_y_all)
                    self.qber_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.qber_x_tab.append(current_time)
                    self.qber_y_tab.append(qber_val)
                    while self.qber_x_tab and self.qber_x_tab[0] < current_time - 60:
                        self.qber_x_tab.pop(0)
                        self.qber_y_tab.pop(0)
                    self.qber_line_tab.setData(self.qber_x_tab, self.qber_y_tab)
                    self.qber_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'kbps_data':
                    kbps = float(data['kbps'])
                    self.kbps_x_all.append(current_time)
                    self.kbps_y_all.append(kbps)
                    while self.kbps_x_all and self.kbps_x_all[0] < current_time - 60:
                        self.kbps_x_all.pop(0)
                        self.kbps_y_all.pop(0)
                    self.kbps_line_all.setData(self.kbps_x_all, self.kbps_y_all)
                    self.kbps_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.kbps_x_tab.append(current_time)
                    self.kbps_y_tab.append(kbps)
                    while self.kbps_x_tab and self.kbps_x_tab[0] < current_time - 60:
                        self.kbps_x_tab.pop(0)
                        self.kbps_y_tab.pop(0)
                    self.kbps_line_tab.setData(self.kbps_x_tab, self.kbps_y_tab)
                    self.kbps_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'key':
                    self.key_display.setText(str(data['value']))

                elif data['type'] == 'visibility':
                    vis_val = float(data['value'])
                    self.visibility_x_all.append(current_time)
                    self.visibility_y_all.append(vis_val)
                    while self.visibility_x_all and self.visibility_x_all[0] < current_time - 60:
                        self.visibility_x_all.pop(0)
                        self.visibility_y_all.pop(0)
                    self.visibility_line_all.setData(self.visibility_x_all, self.visibility_y_all)
                    self.visibility_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.visibility_x_tab.append(current_time)
                    self.visibility_y_tab.append(vis_val)
                    while self.visibility_x_tab and self.visibility_x_tab[0] < current_time - 60:
                        self.visibility_x_tab.pop(0)
                        self.visibility_y_tab.pop(0)
                    self.visibility_line_tab.setData(self.visibility_x_tab, self.visibility_y_tab)
                    self.visibility_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'spd1_decaystate':
                    spd1_val = float(data['value'])
                    self.spd1_x_all.append(current_time)
                    self.spd1_y_all.append(spd1_val)
                    while self.spd1_x_all and self.spd1_x_all[0] < current_time - 60:
                        self.spd1_x_all.pop(0)
                        self.spd1_y_all.pop(0)
                    self.spd1_line_all.setData(self.spd1_x_all, self.spd1_y_all)
                    self.spd1_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.spd1_x_tab.append(current_time)
                    self.spd1_y_tab.append(spd1_val)
                    while self.spd1_x_tab and self.spd1_x_tab[0] < current_time - 60:
                        self.spd1_x_tab.pop(0)
                        self.spd1_y_tab.pop(0)
                    self.spd1_line_tab.setData(self.spd1_x_tab, self.spd1_y_tab)
                    self.spd1_plot_tab.setXRange(max(0, current_time - 60), current_time)

        except Empty:
            pass

    def start_processor(self):
        self.processor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_processor(self):
        self.processor.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        self.processor.close()
        self.marquee_timer.stop()
        event.accept()'''
        
        
        


'''
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QLabel, QTabWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6 import QtCore
from queue import Queue, Empty
import pyqtgraph as pg
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QWidget):
    def __init__(self, data_queue, processor):
        super().__init__()
        self.setObjectName("mainWindow")
        self.data_queue = data_queue
        self.processor = processor
        self.start_time = time.time()
        self.init_ui()
        self.setup_plots()
        self.setup_timer()
        self.setup_marquee()

    def init_ui(self):
        self.setWindowTitle("QUANTUM KEY DISTRIBUTION")
        self.resize(1000, 700)
        self.setMinimumSize(1000, 700)

        self.setStyleSheet("""
            QWidget#mainWindow {
                background-color: #006064;
                color: #F0F4F5;
                font-family: Arial;
            }
            QTabWidget::pane {
                background-color: #006064;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab {
                background-color: #37474F;
                color: #B2EBF2;
                padding: 8px 20px;
                font-size: 12pt;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab:selected {
                background-color: #26A69A;
                color: #F0F4F5;
            }
            QPushButton {
                background-color: #26A69A;
                color: #F0F4F5;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#stopButton {
                background-color: #EF5350;
            }
            QPushButton:hover {
                background-color: #2BBBAD;
            }
            QPushButton#stopButton:hover {
                background-color: #E53935;
            }
            pg.PlotWidget {
                border: 1px solid #B0BEC5;
                background-color: #D1C4E9;
            }
            QLabel#marqueeLabel {
                color: #B2EBF2;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
            QLabel#keyDisplay {
                color: #F0F4F5;
                font-family: Consolas;
                font-size: 10px;
                padding: 5px;
                text-align: center;
                white-space: pre-wrap;
            }
            QWidget#marqueeContainer, QWidget#buttonContainer, QWidget#keyContainer {
                background-color: #37474F;
                border: 1px solid #B0BEC5;
                padding: 5px;
            }
            QWidget#marqueeContainer, QWidget#keyContainer {
                max-height: 80px;
            }
        """)

        main_layout = QVBoxLayout()

        marquee_container = QWidget(objectName="marqueeContainer")
        marquee_layout = QHBoxLayout()
        marquee_layout.addStretch()
        self.marquee_label = QLabel("Welcome To Quantum Key Distribution Output Analyzer   ", objectName="marqueeLabel")
        marquee_layout.addWidget(self.marquee_label)
        marquee_layout.addStretch()
        marquee_container.setLayout(marquee_layout)
        main_layout.addWidget(marquee_container)

        tab_widget = QTabWidget()

        all_tab = QWidget()
        all_layout = QVBoxLayout()

        hist_container_all = QHBoxLayout()
        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        self.hist_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_container_all.addWidget(self.hist_plot_all)

        self.hist2_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist_container_all.addWidget(self.hist2_plot_all)

        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        all_layout.addLayout(hist_container_all)
        all_layout.setStretchFactor(hist_container_all, 3)

        bottom_layout_all = QGridLayout()
        bottom_layout_all.setSpacing(10)

        self.qber_plot_all = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        bottom_layout_all.addWidget(self.qber_plot_all, 0, 0)

        self.kbps_plot_all = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        bottom_layout_all.addWidget(self.kbps_plot_all, 0, 1)

        self.visibility_plot_all = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        bottom_layout_all.addWidget(self.visibility_plot_all, 1, 0)

        self.spd1_plot_all = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        bottom_layout_all.addWidget(self.spd1_plot_all, 1, 1)

        all_layout.addLayout(bottom_layout_all)
        all_layout.setStretchFactor(bottom_layout_all, 2)

        all_tab.setLayout(all_layout)
        tab_widget.addTab(all_tab, "All")

        hist_tab = QWidget()
        hist_tab_layout = QHBoxLayout()
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_tab_layout.addWidget(self.hist_plot_tab)
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist_tab.setLayout(hist_tab_layout)
        tab_widget.addTab(hist_tab, "Histogram (SPD1)")

        hist2_tab = QWidget()
        hist2_tab_layout = QHBoxLayout()
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist2_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist2_tab_layout.addWidget(self.hist2_plot_tab)
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist2_tab.setLayout(hist2_tab_layout)
        tab_widget.addTab(hist2_tab, "Histogram (SPD2)")

        qber_tab = QWidget()
        qber_tab_layout = QHBoxLayout()
        qber_tab_layout.addStretch()
        self.qber_plot_tab = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        self.qber_plot_tab.setFixedSize(600, 400)
        qber_tab_layout.addWidget(self.qber_plot_tab)
        qber_tab_layout.addStretch()
        qber_tab.setLayout(qber_tab_layout)
        tab_widget.addTab(qber_tab, "QBER")

        kbps_tab = QWidget()
        kbps_tab_layout = QHBoxLayout()
        kbps_tab_layout.addStretch()
        self.kbps_plot_tab = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        self.kbps_plot_tab.setFixedSize(600, 400)
        kbps_tab_layout.addWidget(self.kbps_plot_tab)
        kbps_tab_layout.addStretch()
        kbps_tab.setLayout(kbps_tab_layout)
        tab_widget.addTab(kbps_tab, "Throughput")

        visibility_tab = QWidget()
        visibility_tab_layout = QHBoxLayout()
        visibility_tab_layout.addStretch()
        self.visibility_plot_tab = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        self.visibility_plot_tab.setFixedSize(600, 400)
        visibility_tab_layout.addWidget(self.visibility_plot_tab)
        visibility_tab_layout.addStretch()
        visibility_tab.setLayout(visibility_tab_layout)
        tab_widget.addTab(visibility_tab, "Visibility")

        spd1_tab = QWidget()
        spd1_tab_layout = QHBoxLayout()
        spd1_tab_layout.addStretch()
        self.spd1_plot_tab = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        self.spd1_plot_tab.setFixedSize(600, 400)
        spd1_tab_layout.addWidget(self.spd1_plot_tab)
        spd1_tab_layout.addStretch()
        spd1_tab.setLayout(spd1_tab_layout)
        tab_widget.addTab(spd1_tab, "SPD1 Decoy Randomness")

        main_layout.addWidget(tab_widget)

        key_container = QWidget(objectName="keyContainer")
        key_layout = QHBoxLayout()
        key_layout.addStretch()
        self.key_display = QLabel("Key: None", objectName="keyDisplay")
        key_layout.addWidget(self.key_display)
        key_layout.addStretch()
        key_container.setLayout(key_layout)
        main_layout.addWidget(key_container)

        button_container = QWidget(objectName="buttonContainer")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.start_button.clicked.connect(self.start_processor)
        self.stop_button.clicked.connect(self.stop_processor)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def setup_marquee(self):
        self.marquee_timer = QTimer(self)
        self.marquee_timer.setInterval(150)
        self.marquee_timer.timeout.connect(self.update_marquee)
        self.marquee_timer.start()

    def update_marquee(self):
        text = self.marquee_label.text()
        text = text[1:] + text[0]
        self.marquee_label.setText(text)

    def setup_plots(self):
        pg.setConfigOptions(antialias=True)

        def configure_line_plot(plot_widget, y_label, title, x_range=(0, 60), y_range=(0, 10)):
            plot_widget.setLabel('bottom', 'Time (s)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', y_label, color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)
            plot_widget.setYRange(*y_range)

        def configure_histogram_plot(plot_widget, title, brush_color, x_range=(0, 4000)):
            plot_widget.setLabel('bottom', 'Time (ps)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', 'Count', color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)

        self.hist_data_all = np.zeros(40)
        self.hist_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_all, width=100, brush='#FF6F61')
        self.hist_plot_all.addItem(self.hist_bar_all)
        configure_histogram_plot(self.hist_plot_all, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_all = []
        bar_centers = np.arange(40)*100 + 50
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_all[i] + 0.5)
            self.hist_plot_all.addItem(label)
            self.hist_labels_all.append(label)

        self.hist2_data_all = np.zeros(40)
        self.hist2_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_all, width=100, brush='#FFCA28')
        self.hist2_plot_all.addItem(self.hist2_bar_all)
        configure_histogram_plot(self.hist2_plot_all, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_all = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_all[i] + 0.5)
            self.hist2_plot_all.addItem(label)
            self.hist2_labels_all.append(label)

        self.hist_data_tab = np.zeros(40)
        self.hist_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_tab, width=100, brush='#FF6F61')
        self.hist_plot_tab.addItem(self.hist_bar_tab)
        configure_histogram_plot(self.hist_plot_tab, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_tab[i] + 0.5)
            self.hist_plot_tab.addItem(label)
            self.hist_labels_tab.append(label)

        self.hist2_data_tab = np.zeros(40)
        self.hist2_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_tab, width=100, brush='#FFCA28')
        self.hist2_plot_tab.addItem(self.hist2_bar_tab)
        configure_histogram_plot(self.hist2_plot_tab, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_tab[i] + 0.5)
            self.hist2_plot_tab.addItem(label)
            self.hist2_labels_tab.append(label)

        self.qber_x_all = []
        self.qber_y_all = []
        self.qber_line_all = self.qber_plot_all.plot(self.qber_x_all, self.qber_y_all, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_all, 'QBER (%)', "Quantum Bit Error Rate")

        self.qber_x_tab = []
        self.qber_y_tab = []
        self.qber_line_tab = self.qber_plot_tab.plot(self.qber_x_tab, self.qber_y_tab, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_tab, 'QBER (%)', "Quantum Bit Error Rate")

        self.kbps_x_all = []
        self.kbps_y_all = []
        self.kbps_line_all = self.kbps_plot_all.plot(self.kbps_x_all, self.kbps_y_all, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_all, 'kbps', "Throughput (kbps)")

        self.kbps_x_tab = []
        self.kbps_y_tab = []
        self.kbps_line_tab = self.kbps_plot_tab.plot(self.kbps_x_tab, self.kbps_y_tab, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_tab, 'kbps', "Throughput (kbps)")

        self.visibility_x_all = []
        self.visibility_y_all = []
        self.visibility_line_all = self.visibility_plot_all.plot(self.visibility_x_all, self.visibility_y_all, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_all, 'Ratio', "Visibility Ratio")

        self.visibility_x_tab = []
        self.visibility_y_tab = []
        self.visibility_line_tab = self.visibility_plot_tab.plot(self.visibility_x_tab, self.visibility_y_tab, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_tab, 'Ratio', "Visibility Ratio")

        self.spd1_x_all = []
        self.spd1_y_all = []
        self.spd1_line_all = self.spd1_plot_all.plot(self.spd1_x_all, self.spd1_y_all, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_all, 'Value', "SPD1 Decoy Randomness")

        self.spd1_x_tab = []
        self.spd1_y_tab = []
        self.spd1_line_tab = self.spd1_plot_tab.plot(self.spd1_x_tab, self.spd1_y_tab, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_tab, 'Value', "SPD1 Decoy Randomness")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

    def update_plots(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                current_time = time.time() - self.start_time
                logging.debug(f"Processing data: {data}")

                if data['type'] == 'timestamp_spd1':
                    timestamp_ps = int(data['value'])
                    logging.debug(f"SPD1 timestamp: {timestamp_ps}")
                    partition1 = min((timestamp_ps // 100) % 40, 39)
                    self.hist_data_all[partition1] += 1
                    self.hist_bar_all.setOpts(height=self.hist_data_all)
                    self.hist_labels_all[partition1].setText(str(int(self.hist_data_all[partition1])))
                    self.hist_labels_all[partition1].setPos(partition1*100 + 50, self.hist_data_all[partition1] + 0.5)
                    self.hist_plot_all.setYRange(0, max(self.hist_data_all.max() * 1.2, 10))
                    logging.debug(f"SPD1 histogram data: {self.hist_data_all}")

                    self.hist_data_tab[partition1] += 1
                    self.hist_bar_tab.setOpts(height=self.hist_data_tab)
                    self.hist_labels_tab[partition1].setText(str(int(self.hist_data_tab[partition1])))
                    self.hist_labels_tab[partition1].setPos(partition1*100 + 50, self.hist_data_tab[partition1] + 0.5)
                    self.hist_plot_tab.setYRange(0, max(self.hist_data_tab.max() * 1.2, 10))
                    logging.debug(f"SPD1 tab histogram data: {self.hist_data_tab}")

                elif data['type'] == 'timestamp_spd2':
                    timestamp_ps = int(data['value'])
                    logging.debug(f"SPD2 timestamp: {timestamp_ps}")
                    partition2 = min((timestamp_ps // 100) % 40, 39)
                    self.hist2_data_all[partition2] += 1
                    self.hist2_bar_all.setOpts(height=self.hist2_data_all)
                    self.hist2_labels_all[partition2].setText(str(int(self.hist2_data_all[partition2])))
                    self.hist2_labels_all[partition2].setPos(partition2*100 + 50, self.hist2_data_all[partition2] + 0.5)
                    self.hist2_plot_all.setYRange(0, max(self.hist2_data_all.max() * 1.2, 10))
                    logging.debug(f"SPD2 histogram data: {self.hist2_data_all}")

                    self.hist2_data_tab[partition2] += 1
                    self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
                    self.hist2_labels_tab[partition2].setText(str(int(self.hist2_data_tab[partition2])))
                    self.hist2_labels_tab[partition2].setPos(partition2*100 + 50, self.hist2_data_tab[partition2] + 0.5)
                    self.hist2_plot_tab.setYRange(0, max(self.hist2_data_tab.max() * 1.2, 10))
                    logging.debug(f"SPD2 tab histogram data: {self.hist2_data_tab}")

                elif data['type'] == 'qber':
                    qber_val = float(data['value'])
                    logging.debug(f"QBER: {qber_val}")
                    self.qber_x_all.append(current_time)
                    self.qber_y_all.append(qber_val)
                    while self.qber_x_all and self.qber_x_all[0] < current_time - 60:
                        self.qber_x_all.pop(0)
                        self.qber_y_all.pop(0)
                    self.qber_line_all.setData(self.qber_x_all, self.qber_y_all)
                    self.qber_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.qber_x_tab.append(current_time)
                    self.qber_y_tab.append(qber_val)
                    while self.qber_x_tab and self.qber_x_tab[0] < current_time - 60:
                        self.qber_x_tab.pop(0)
                        self.qber_y_tab.pop(0)
                    self.qber_line_tab.setData(self.qber_x_tab, self.qber_y_tab)
                    self.qber_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'kbps_data':
                    kbps = float(data['kbps'])
                    logging.debug(f"KBPS: {kbps}")
                    self.kbps_x_all.append(current_time)
                    self.kbps_y_all.append(kbps)
                    while self.kbps_x_all and self.kbps_x_all[0] < current_time - 60:
                        self.kbps_x_all.pop(0)
                        self.kbps_y_all.pop(0)
                    self.kbps_line_all.setData(self.kbps_x_all, self.kbps_y_all)
                    self.kbps_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.kbps_x_tab.append(current_time)
                    self.kbps_y_tab.append(kbps)
                    while self.kbps_x_tab and self.kbps_x_tab[0] < current_time - 60:
                        self.kbps_x_tab.pop(0)
                        self.kbps_y_tab.pop(0)
                    self.kbps_line_tab.setData(self.kbps_x_tab, self.kbps_y_tab)
                    self.kbps_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'key':
                    logging.debug(f"Key: {data['value'][:40]}...")
                    self.key_display.setText(f"Key: {data['value']}")

                elif data['type'] == 'visibility':
                    vis_val = float(data['value'])
                    logging.debug(f"Visibility: {vis_val}")
                    self.visibility_x_all.append(current_time)
                    self.visibility_y_all.append(vis_val)
                    while self.visibility_x_all and self.visibility_x_all[0] < current_time - 60:
                        self.visibility_x_all.pop(0)
                        self.visibility_y_all.pop(0)
                    self.visibility_line_all.setData(self.visibility_x_all, self.visibility_y_all)
                    self.visibility_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.visibility_x_tab.append(current_time)
                    self.visibility_y_tab.append(vis_val)
                    while self.visibility_x_tab and self.visibility_x_tab[0] < current_time - 60:
                        self.visibility_x_tab.pop(0)
                        self.visibility_y_tab.pop(0)
                    self.visibility_line_tab.setData(self.visibility_x_tab, self.visibility_y_tab)
                    self.visibility_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'spd1_decaystate':
                    spd1_val = float(data['value'])
                    logging.debug(f"SPD1 Decay: {spd1_val}")
                    self.spd1_x_all.append(current_time)
                    self.spd1_y_all.append(spd1_val)
                    while self.spd1_x_all and self.spd1_x_all[0] < current_time - 60:
                        self.spd1_x_all.pop(0)
                        self.spd1_y_all.pop(0)
                    self.spd1_line_all.setData(self.spd1_x_all, self.spd1_y_all)
                    self.spd1_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.spd1_x_tab.append(current_time)
                    self.spd1_y_tab.append(spd1_val)
                    while self.spd1_x_tab and self.spd1_x_tab[0] < current_time - 60:
                        self.spd1_x_tab.pop(0)
                        self.spd1_y_tab.pop(0)
                    self.spd1_line_tab.setData(self.spd1_x_tab, self.spd1_y_tab)
                    self.spd1_plot_tab.setXRange(max(0, current_time - 60), current_time)

        except Empty:
            pass

    def start_processor(self):
        logging.info("Starting processor")
        self.processor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_time = time.time()
        # Temporarily disable histogram reset to test data accumulation
        # self.hist_data_all.fill(0)
        # self.hist_data_tab.fill(0)
        # self.hist2_data_all.fill(0)
        # self.hist2_data_tab.fill(0)
        # self.hist_bar_all.setOpts(height=self.hist_data_all)
        # self.hist_bar_tab.setOpts(height=self.hist_data_tab)
        # self.hist2_bar_all.setOpts(height=self.hist2_data_all)
        # self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
        # for i in range(40):
        #     self.hist_labels_all[i].setText("0")
        #     self.hist_labels_all[i].setPos(i*100 + 50, 0.5)
        #     self.hist_labels_tab[i].setText("0")
        #     self.hist_labels_tab[i].setPos(i*100 + 50, 0.5)
        #     self.hist2_labels_all[i].setText("0")
        #     self.hist2_labels_all[i].setPos(i*100 + 50, 0.5)
        #     self.hist2_labels_tab[i].setText("0")
        #     self.hist2_labels_tab[i].setPos(i*100 + 50, 0.5)

    def stop_processor(self):
        logging.info("Stopping processor")
        self.processor.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        logging.info("Closing window")
        self.processor.close()
        self.marquee_timer.stop()
        event.accept()'''
        
        
        
        
'''      
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QLabel, QTabWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6 import QtCore
from queue import Queue, Empty
import pyqtgraph as pg
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QWidget):
    def __init__(self, data_queue, processor):
        super().__init__()
        self.setObjectName("mainWindow")
        self.data_queue = data_queue
        self.processor = processor
        self.start_time = time.time()
        self.current_session = -1
        self.session_data_types = set()
        self.init_ui()
        self.setup_plots()
        self.setup_timer()
        self.setup_marquee()

    def init_ui(self):
        self.setWindowTitle("QUANTUM KEY DISTRIBUTION")
        self.resize(1000, 700)
        self.setMinimumSize(1000, 700)

        self.setStyleSheet("""
            QWidget#mainWindow {
                background-color: #006064;
                color: #F0F4F5;
                font-family: Arial;
            }
            QTabWidget::pane {
                background-color: #006064;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab {
                background-color: #37474F;
                color: #B2EBF2;
                padding: 8px 20px;
                font-size: 12pt;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab:selected {
                background-color: #26A69A;
                color: #F0F4F5;
            }
            QPushButton {
                background-color: #26A69A;
                color: #F0F4F5;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#stopButton {
                background-color: #EF5350;
            }
            QPushButton:hover {
                background-color: #2BBBAD;
            }
            QPushButton#stopButton:hover {
                background-color: #E53935;
            }
            pg.PlotWidget {
                border: 1px solid #B0BEC5;
                background-color: #D1C4E9;
            }
            QLabel#marqueeLabel {
                color: #B2EBF2;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
            QLabel#keyDisplay {
                color: #F0F4F5;
                font-family: Consolas;
                font-size: 10px;
                padding: 5px;
                text-align: center;
                white-space: pre-wrap;
            }
            QWidget#marqueeContainer, QWidget#buttonContainer, QWidget#keyContainer {
                background-color: #37474F;
                border: 1px solid #B0BEC5;
                padding: 5px;
            }
            QWidget#marqueeContainer, QWidget#keyContainer {
                max-height: 80px;
            }
        """)

        main_layout = QVBoxLayout()

        marquee_container = QWidget(objectName="marqueeContainer")
        marquee_layout = QHBoxLayout()
        marquee_layout.addStretch()
        self.marquee_label = QLabel("Welcome To Quantum Key Distribution Output Analyzer   ", objectName="marqueeLabel")
        marquee_layout.addWidget(self.marquee_label)
        marquee_layout.addStretch()
        marquee_container.setLayout(marquee_layout)
        main_layout.addWidget(marquee_container)

        tab_widget = QTabWidget()

        all_tab = QWidget()
        all_layout = QVBoxLayout()

        hist_container_all = QHBoxLayout()
        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        self.hist_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_container_all.addWidget(self.hist_plot_all)

        self.hist2_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist_container_all.addWidget(self.hist2_plot_all)

        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        all_layout.addLayout(hist_container_all)
        all_layout.setStretchFactor(hist_container_all, 3)

        bottom_layout_all = QGridLayout()
        bottom_layout_all.setSpacing(10)

        self.qber_plot_all = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        bottom_layout_all.addWidget(self.qber_plot_all, 0, 0)

        self.kbps_plot_all = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        bottom_layout_all.addWidget(self.kbps_plot_all, 0, 1)

        self.visibility_plot_all = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        bottom_layout_all.addWidget(self.visibility_plot_all, 1, 0)

        self.spd1_plot_all = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        bottom_layout_all.addWidget(self.spd1_plot_all, 1, 1)

        all_layout.addLayout(bottom_layout_all)
        all_layout.setStretchFactor(bottom_layout_all, 2)

        all_tab.setLayout(all_layout)
        tab_widget.addTab(all_tab, "All")

        hist_tab = QWidget()
        hist_tab_layout = QHBoxLayout()
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_tab_layout.addWidget(self.hist_plot_tab)
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist_tab.setLayout(hist_tab_layout)
        tab_widget.addTab(hist_tab, "Histogram (SPD1)")

        hist2_tab = QWidget()
        hist2_tab_layout = QHBoxLayout()
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist2_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist2_tab_layout.addWidget(self.hist2_plot_tab)
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist2_tab.setLayout(hist2_tab_layout)
        tab_widget.addTab(hist2_tab, "Histogram (SPD2)")

        qber_tab = QWidget()
        qber_tab_layout = QHBoxLayout()
        qber_tab_layout.addStretch()
        self.qber_plot_tab = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        self.qber_plot_tab.setFixedSize(600, 400)
        qber_tab_layout.addWidget(self.qber_plot_tab)
        qber_tab_layout.addStretch()
        qber_tab.setLayout(qber_tab_layout)
        tab_widget.addTab(qber_tab, "QBER")

        kbps_tab = QWidget()
        kbps_tab_layout = QHBoxLayout()
        kbps_tab_layout.addStretch()
        self.kbps_plot_tab = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        self.kbps_plot_tab.setFixedSize(600, 400)
        kbps_tab_layout.addWidget(self.kbps_plot_tab)
        kbps_tab_layout.addStretch()
        kbps_tab.setLayout(kbps_tab_layout)
        tab_widget.addTab(kbps_tab, "Throughput")

        visibility_tab = QWidget()
        visibility_tab_layout = QHBoxLayout()
        visibility_tab_layout.addStretch()
        self.visibility_plot_tab = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        self.visibility_plot_tab.setFixedSize(600, 400)
        visibility_tab_layout.addWidget(self.visibility_plot_tab)
        visibility_tab_layout.addStretch()
        visibility_tab.setLayout(visibility_tab_layout)
        tab_widget.addTab(visibility_tab, "Visibility")

        spd1_tab = QWidget()
        spd1_tab_layout = QHBoxLayout()
        spd1_tab_layout.addStretch()
        self.spd1_plot_tab = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        self.spd1_plot_tab.setFixedSize(600, 400)
        spd1_tab_layout.addWidget(self.spd1_plot_tab)
        spd1_tab_layout.addStretch()
        spd1_tab.setLayout(spd1_tab_layout)
        tab_widget.addTab(spd1_tab, "SPD1 Decoy Randomness")

        main_layout.addWidget(tab_widget)

        key_container = QWidget(objectName="keyContainer")
        key_layout = QHBoxLayout()
        key_layout.addStretch()
        self.key_display = QLabel("Key: None", objectName="keyDisplay")
        key_layout.addWidget(self.key_display)
        key_layout.addStretch()
        key_container.setLayout(key_layout)
        main_layout.addWidget(key_container)

        button_container = QWidget(objectName="buttonContainer")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.start_button.clicked.connect(self.start_processor)
        self.stop_button.clicked.connect(self.stop_processor)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def setup_marquee(self):
        self.marquee_timer = QTimer(self)
        self.marquee_timer.setInterval(150)
        self.marquee_timer.timeout.connect(self.update_marquee)
        self.marquee_timer.start()

    def update_marquee(self):
        text = self.marquee_label.text()
        text = text[1:] + text[0]
        self.marquee_label.setText(text)

    def setup_plots(self):
        pg.setConfigOptions(antialias=True)

        def configure_line_plot(plot_widget, y_label, title, x_range=(0, 60), y_range=(0, 10)):
            plot_widget.setLabel('bottom', 'Time (s)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', y_label, color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)
            plot_widget.setYRange(*y_range)

        def configure_histogram_plot(plot_widget, title, brush_color, x_range=(0, 4000)):
            plot_widget.setLabel('bottom', 'Time (ps)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', 'Count', color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)

        self.hist_data_all = np.zeros(40)
        self.hist_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_all, width=100, brush='#FF6F61')
        self.hist_plot_all.addItem(self.hist_bar_all)
        configure_histogram_plot(self.hist_plot_all, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_all = []
        bar_centers = np.arange(40)*100 + 50
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_all[i] + 0.5)
            self.hist_plot_all.addItem(label)
            self.hist_labels_all.append(label)

        self.hist2_data_all = np.zeros(40)
        self.hist2_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_all, width=100, brush='#FFCA28')
        self.hist2_plot_all.addItem(self.hist2_bar_all)
        configure_histogram_plot(self.hist2_plot_all, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_all = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_all[i] + 0.5)
            self.hist2_plot_all.addItem(label)
            self.hist2_labels_all.append(label)

        self.hist_data_tab = np.zeros(40)
        self.hist_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_tab, width=100, brush='#FF6F61')
        self.hist_plot_tab.addItem(self.hist_bar_tab)
        configure_histogram_plot(self.hist_plot_tab, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_tab[i] + 0.5)
            self.hist_plot_tab.addItem(label)
            self.hist_labels_tab.append(label)

        self.hist2_data_tab = np.zeros(40)
        self.hist2_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_tab, width=100, brush='#FFCA28')
        self.hist2_plot_tab.addItem(self.hist2_bar_tab)
        configure_histogram_plot(self.hist2_plot_tab, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_tab[i] + 0.5)
            self.hist2_plot_tab.addItem(label)
            self.hist2_labels_tab.append(label)

        self.qber_x_all = []
        self.qber_y_all = []
        self.qber_line_all = self.qber_plot_all.plot(self.qber_x_all, self.qber_y_all, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_all, 'QBER (%)', "Quantum Bit Error Rate")

        self.qber_x_tab = []
        self.qber_y_tab = []
        self.qber_line_tab = self.qber_plot_tab.plot(self.qber_x_tab, self.qber_y_tab, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_tab, 'QBER (%)', "Quantum Bit Error Rate")

        self.kbps_x_all = []
        self.kbps_y_all = []
        self.kbps_line_all = self.kbps_plot_all.plot(self.kbps_x_all, self.kbps_y_all, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_all, 'kbps', "Throughput (kbps)")

        self.kbps_x_tab = []
        self.kbps_y_tab = []
        self.kbps_line_tab = self.kbps_plot_tab.plot(self.kbps_x_tab, self.kbps_y_tab, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_tab, 'kbps', "Throughput (kbps)")

        self.visibility_x_all = []
        self.visibility_y_all = []
        self.visibility_line_all = self.visibility_plot_all.plot(self.visibility_x_all, self.visibility_y_all, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_all, 'Ratio', "Visibility Ratio")

        self.visibility_x_tab = []
        self.visibility_y_tab = []
        self.visibility_line_tab = self.visibility_plot_tab.plot(self.visibility_x_tab, self.visibility_y_tab, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_tab, 'Ratio', "Visibility Ratio")

        self.spd1_x_all = []
        self.spd1_y_all = []
        self.spd1_line_all = self.spd1_plot_all.plot(self.spd1_x_all, self.spd1_y_all, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_all, 'Value', "SPD1 Decoy Randomness")

        self.spd1_x_tab = []
        self.spd1_y_tab = []
        self.spd1_line_tab = self.spd1_plot_tab.plot(self.spd1_x_tab, self.spd1_y_tab, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_tab, 'Value', "SPD1 Decoy Randomness")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

    def update_plots(self):
        try:
            for _ in range(100):
                data = self.data_queue.get_nowait()
                current_time = time.time() - self.start_time
                logging.debug(f"Processing data: {data}")

                if data['type'] == 'session_number':
                    new_session = data['value']
                    if new_session != self.current_session:
                        # Log missing data types from previous session
                        expected_types = {'timestamp_spd1', 'timestamp_spd2', 'spd1_decaystate', 'visibility', 'qber', 'key', 'kbps_data'}
                        missing_types = expected_types - self.session_data_types
                        if missing_types and self.current_session != -1:
                            logging.warning(f"Session {self.current_session} missing data types: {missing_types}")
                            if 'key' not in self.session_data_types:
                                self.key_display.setText("Key: Not Available")
                        self.current_session = new_session
                        self.session_data_types = set()
                    continue

                self.session_data_types.add(data['type'])

                if data['type'] == 'timestamp_spd1':
                    timestamp_ps = int(data['value'])
                    logging.debug(f"SPD1 timestamp: {timestamp_ps}")
                    partition1 = min((timestamp_ps // 100) % 40, 39)
                    self.hist_data_all[partition1] += 1
                    self.hist_bar_all.setOpts(height=self.hist_data_all)
                    self.hist_labels_all[partition1].setText(str(int(self.hist_data_all[partition1])))
                    self.hist_labels_all[partition1].setPos(partition1*100 + 50, self.hist_data_all[partition1] + 0.5)
                    self.hist_plot_all.setYRange(0, max(self.hist_data_all.max() * 1.2, 10))
                    logging.debug(f"SPD1 histogram data: {self.hist_data_all}")

                    self.hist_data_tab[partition1] += 1
                    self.hist_bar_tab.setOpts(height=self.hist_data_tab)
                    self.hist_labels_tab[partition1].setText(str(int(self.hist_data_tab[partition1])))
                    self.hist_labels_tab[partition1].setPos(partition1*100 + 50, self.hist_data_tab[partition1] + 0.5)
                    self.hist_plot_tab.setYRange(0, max(self.hist_data_tab.max() * 1.2, 10))
                    logging.debug(f"SPD1 tab histogram data: {self.hist_data_tab}")

                elif data['type'] == 'timestamp_spd2':
                    timestamp_ps = int(data['value'])
                    logging.debug(f"SPD2 timestamp: {timestamp_ps}")
                    partition2 = min((timestamp_ps // 100) % 40, 39)
                    self.hist2_data_all[partition2] += 1
                    self.hist2_bar_all.setOpts(height=self.hist2_data_all)
                    self.hist2_labels_all[partition2].setText(str(int(self.hist2_data_all[partition2])))
                    self.hist2_labels_all[partition2].setPos(partition2*100 + 50, self.hist2_data_all[partition2] + 0.5)
                    self.hist2_plot_all.setYRange(0, max(self.hist2_data_all.max() * 1.2, 10))
                    logging.debug(f"SPD2 histogram data: {self.hist2_data_all}")

                    self.hist2_data_tab[partition2] += 1
                    self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
                    self.hist2_labels_tab[partition2].setText(str(int(self.hist2_data_tab[partition2])))
                    self.hist2_labels_tab[partition2].setPos(partition2*100 + 50, self.hist2_data_tab[partition2] + 0.5)
                    self.hist2_plot_tab.setYRange(0, max(self.hist2_data_tab.max() * 1.2, 10))
                    logging.debug(f"SPD2 tab histogram data: {self.hist2_data_tab}")

                elif data['type'] == 'qber':
                    qber_val = float(data['value'])
                    logging.debug(f"QBER: {qber_val}")
                    self.qber_x_all.append(current_time)
                    self.qber_y_all.append(qber_val)
                    while self.qber_x_all and self.qber_x_all[0] < current_time - 60:
                        self.qber_x_all.pop(0)
                        self.qber_y_all.pop(0)
                    self.qber_line_all.setData(self.qber_x_all, self.qber_y_all)
                    self.qber_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.qber_x_tab.append(current_time)
                    self.qber_y_tab.append(qber_val)
                    while self.qber_x_tab and self.qber_x_tab[0] < current_time - 60:
                        self.qber_x_tab.pop(0)
                        self.qber_y_tab.pop(0)
                    self.qber_line_tab.setData(self.qber_x_tab, self.qber_y_tab)
                    self.qber_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'kbps_data':
                    kbps = float(data['kbps'])
                    logging.debug(f"KBPS: {kbps}")
                    self.kbps_x_all.append(current_time)
                    self.kbps_y_all.append(kbps)
                    while self.kbps_x_all and self.kbps_x_all[0] < current_time - 60:
                        self.kbps_x_all.pop(0)
                        self.kbps_y_all.pop(0)
                    self.kbps_line_all.setData(self.kbps_x_all, self.kbps_y_all)
                    self.kbps_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.kbps_x_tab.append(current_time)
                    self.kbps_y_tab.append(kbps)
                    while self.kbps_x_tab and self.kbps_x_tab[0] < current_time - 60:
                        self.kbps_x_tab.pop(0)
                        self.kbps_y_tab.pop(0)
                    self.kbps_line_tab.setData(self.kbps_x_tab, self.kbps_y_tab)
                    self.kbps_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'key':
                    logging.debug(f"Key: {data['value'][:40]}...")
                    self.key_display.setText(f"Key: {data['value']}")

                elif data['type'] == 'visibility':
                    vis_val = float(data['value'])
                    logging.debug(f"Visibility: {vis_val}")
                    self.visibility_x_all.append(current_time)
                    self.visibility_y_all.append(vis_val)
                    while self.visibility_x_all and self.visibility_x_all[0] < current_time - 60:
                        self.visibility_x_all.pop(0)
                        self.visibility_y_all.pop(0)
                    self.visibility_line_all.setData(self.visibility_x_all, self.visibility_y_all)
                    self.visibility_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.visibility_x_tab.append(current_time)
                    self.visibility_y_tab.append(vis_val)
                    while self.visibility_x_tab and self.visibility_x_tab[0] < current_time - 60:
                        self.visibility_x_tab.pop(0)
                        self.visibility_y_tab.pop(0)
                    self.visibility_line_tab.setData(self.visibility_x_tab, self.visibility_y_tab)
                    self.visibility_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'spd1_decaystate':
                    spd1_val = float(data['value'])
                    logging.debug(f"SPD1 Decay: {spd1_val}")
                    self.spd1_x_all.append(current_time)
                    self.spd1_y_all.append(spd1_val)
                    while self.spd1_x_all and self.spd1_x_all[0] < current_time - 60:
                        self.spd1_x_all.pop(0)
                        self.spd1_y_all.pop(0)
                    self.spd1_line_all.setData(self.spd1_x_all, self.spd1_y_all)
                    self.spd1_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.spd1_x_tab.append(current_time)
                    self.spd1_y_tab.append(spd1_val)
                    while self.spd1_x_tab and self.spd1_x_tab[0] < current_time - 60:
                        self.spd1_x_tab.pop(0)
                        self.spd1_y_tab.pop(0)
                    self.spd1_line_tab.setData(self.spd1_x_tab, self.spd1_y_tab)
                    self.spd1_plot_tab.setXRange(max(0, current_time - 60), current_time)

        except Empty:
            pass

    def start_processor(self):
        logging.info("Starting processor")
        self.processor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_time = time.time()
        self.current_session = -1
        self.session_data_types = set()
        self.key_display.setText("Key: None")
        # Temporarily disable histogram reset to test data accumulation
        # self.hist_data_all.fill(0)
        # self.hist_data_tab.fill(0)
        # self.hist2_data_all.fill(0)
        # self.hist2_data_tab.fill(0)
        # self.hist_bar_all.setOpts(height=self.hist_data_all)
        # self.hist_bar_tab.setOpts(height=self.hist_data_tab)
        # self.hist2_bar_all.setOpts(height=self.hist2_data_all)
        # self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
        # for i in range(40):
        #     self.hist_labels_all[i].setText("0")
        #     self.hist_labels_all[i].setPos(i*100 + 50, 0.5)
        #     self.hist_labels_tab[i].setText("0")
        #     self.hist_labels_tab[i].setPos(i*100 + 50, 0.5)
        #     self.hist2_labels_all[i].setText("0")
        #     self.hist2_labels_all[i].setPos(i*100 + 50, 0.5)
        #     self.hist2_labels_tab[i].setText("0")
        #     self.hist2_labels_tab[i].setPos(i*100 + 50, 0.5)

    def stop_processor(self):
        logging.info("Stopping processor")
        self.processor.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        logging.info("Closing window")
        self.processor.close()
        self.marquee_timer.stop()
        event.accept()'''
        
        


import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QLabel, QTabWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6 import QtCore
from queue import Queue, Empty
import pyqtgraph as pg
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QWidget):
    def __init__(self, data_queue, processor):
        super().__init__()
        self.setObjectName("mainWindow")
        self.data_queue = data_queue
        self.processor = processor
        self.start_time = time.time()
        self.current_session = -1
        self.session_data_types = set()
        self.init_ui()
        self.setup_plots()
        self.setup_timer()
        self.setup_marquee()

    def init_ui(self):
        self.setWindowTitle("QUANTUM KEY DISTRIBUTION")
        self.resize(1000, 700)
        self.setMinimumSize(1000, 700)

        self.setStyleSheet("""
            QWidget#mainWindow {
                background-color: #006064;
                color: #F0F4F5;
                font-family: Arial;
            }
            QTabWidget::pane {
                background-color: #006064;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab {
                background-color: #37474F;
                color: #B2EBF2;
                padding: 8px 20px;
                font-size: 12pt;
                border: 1px solid #B0BEC5;
            }
            QTabBar::tab:selected {
                background-color: #26A69A;
                color: #F0F4F5;
            }
            QPushButton {
                background-color: #26A69A;
                color: #F0F4F5;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#stopButton {
                background-color: #EF5350;
            }
            QPushButton:hover {
                background-color: #2BBBAD;
            }
            QPushButton#stopButton:hover {
                background-color: #E53935;
            }
            pg.PlotWidget {
                border: 1px solid #B0BEC5;
                background-color: #D1C4E9;
            }
            QLabel#marqueeLabel {
                color: #B2EBF2;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
            QLabel#keyDisplay {
                color: #F0F4F5;
                font-family: Consolas;
                font-size: 10px;
                padding: 5px;
                text-align: center;
                white-space: pre-wrap;
            }
            QWidget#marqueeContainer, QWidget#buttonContainer, QWidget#keyContainer {
                background-color: #37474F;
                border: 1px solid #B0BEC5;
                padding: 5px;
            }
            QWidget#marqueeContainer, QWidget#keyContainer {
                max-height: 80px;
            }
        """)

        main_layout = QVBoxLayout()

        marquee_container = QWidget(objectName="marqueeContainer")
        marquee_layout = QHBoxLayout()
        marquee_layout.addStretch()
        self.marquee_label = QLabel("Welcome To Quantum Key Distribution Output Analyzer   ", objectName="marqueeLabel")
        marquee_layout.addWidget(self.marquee_label)
        marquee_layout.addStretch()
        marquee_container.setLayout(marquee_layout)
        main_layout.addWidget(marquee_container)

        tab_widget = QTabWidget()

        all_tab = QWidget()
        all_layout = QVBoxLayout()

        hist_container_all = QHBoxLayout()
        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

        self.hist_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_container_all.addWidget(self.hist_plot_all)

        self.hist2_plot_all = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist_container_all.addWidget(self.hist2_plot_all)

        hist_container_all.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        all_layout.addLayout(hist_container_all)
        all_layout.setStretchFactor(hist_container_all, 3)

        bottom_layout_all = QGridLayout()
        bottom_layout_all.setSpacing(10)

        self.qber_plot_all = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        bottom_layout_all.addWidget(self.qber_plot_all, 0, 0)

        self.kbps_plot_all = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        bottom_layout_all.addWidget(self.kbps_plot_all, 0, 1)

        self.visibility_plot_all = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        bottom_layout_all.addWidget(self.visibility_plot_all, 1, 0)

        self.spd1_plot_all = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        bottom_layout_all.addWidget(self.spd1_plot_all, 1, 1)

        all_layout.addLayout(bottom_layout_all)
        all_layout.setStretchFactor(bottom_layout_all, 2)

        all_tab.setLayout(all_layout)
        tab_widget.addTab(all_tab, "All")

        hist_tab = QWidget()
        hist_tab_layout = QHBoxLayout()
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD1)", objectName="histPlot")
        hist_tab_layout.addWidget(self.hist_plot_tab)
        hist_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist_tab.setLayout(hist_tab_layout)
        tab_widget.addTab(hist_tab, "Histogram (SPD1)")

        hist2_tab = QWidget()
        hist2_tab_layout = QHBoxLayout()
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        self.hist2_plot_tab = pg.PlotWidget(title="Timestamp Histogram (SPD2)", objectName="hist2Plot")
        hist2_tab_layout.addWidget(self.hist2_plot_tab)
        hist2_tab_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        hist2_tab.setLayout(hist2_tab_layout)
        tab_widget.addTab(hist2_tab, "Histogram (SPD2)")

        qber_tab = QWidget()
        qber_tab_layout = QHBoxLayout()
        qber_tab_layout.addStretch()
        self.qber_plot_tab = pg.PlotWidget(title="Quantum Bit Error Rate", objectName="qberPlot")
        self.qber_plot_tab.setFixedSize(600, 400)
        qber_tab_layout.addWidget(self.qber_plot_tab)
        qber_tab_layout.addStretch()
        qber_tab.setLayout(qber_tab_layout)
        tab_widget.addTab(qber_tab, "QBER")

        kbps_tab = QWidget()
        kbps_tab_layout = QHBoxLayout()
        kbps_tab_layout.addStretch()
        self.kbps_plot_tab = pg.PlotWidget(title="Throughput (kbps)", objectName="kbpsPlot")
        self.kbps_plot_tab.setFixedSize(600, 400)
        kbps_tab_layout.addWidget(self.kbps_plot_tab)
        kbps_tab_layout.addStretch()
        kbps_tab.setLayout(kbps_tab_layout)
        tab_widget.addTab(kbps_tab, "Throughput")

        visibility_tab = QWidget()
        visibility_tab_layout = QHBoxLayout()
        visibility_tab_layout.addStretch()
        self.visibility_plot_tab = pg.PlotWidget(title="Visibility Ratio", objectName="visibilityPlot")
        self.visibility_plot_tab.setFixedSize(600, 400)
        visibility_tab_layout.addWidget(self.visibility_plot_tab)
        visibility_tab_layout.addStretch()
        visibility_tab.setLayout(visibility_tab_layout)
        tab_widget.addTab(visibility_tab, "Visibility")

        spd1_tab = QWidget()
        spd1_tab_layout = QHBoxLayout()
        spd1_tab_layout.addStretch()
        self.spd1_plot_tab = pg.PlotWidget(title="SPD1 Decoy Randomness", objectName="spd1Plot")
        self.spd1_plot_tab.setFixedSize(600, 400)
        spd1_tab_layout.addWidget(self.spd1_plot_tab)
        spd1_tab_layout.addStretch()
        spd1_tab.setLayout(spd1_tab_layout)
        tab_widget.addTab(spd1_tab, "SPD1 Decoy Randomness")

        main_layout.addWidget(tab_widget)

        key_container = QWidget(objectName="keyContainer")
        key_layout = QHBoxLayout()
        key_layout.addStretch()
        self.key_display = QLabel("Key (None): None", objectName="keyDisplay")
        key_layout.addWidget(self.key_display)
        key_layout.addStretch()
        key_container.setLayout(key_layout)
        main_layout.addWidget(key_container)

        button_container = QWidget(objectName="buttonContainer")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.start_button.clicked.connect(self.start_processor)
        self.stop_button.clicked.connect(self.stop_processor)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def setup_marquee(self):
        self.marquee_timer = QTimer(self)
        self.marquee_timer.setInterval(150)
        self.marquee_timer.timeout.connect(self.update_marquee)
        self.marquee_timer.start()

    def update_marquee(self):
        text = self.marquee_label.text()
        text = text[1:] + text[0]
        self.marquee_label.setText(text)

    def setup_plots(self):
        pg.setConfigOptions(antialias=True)

        def configure_line_plot(plot_widget, y_label, title, x_range=(0, 60), y_range=(0, 10)):
            plot_widget.setLabel('bottom', 'Time (s)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', y_label, color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)
            plot_widget.setYRange(*y_range)

        def configure_histogram_plot(plot_widget, title, brush_color, x_range=(0, 4000)):
            plot_widget.setLabel('bottom', 'Time (ps)', color='#F0F4F5', size='12pt')
            plot_widget.setLabel('left', 'Count', color='#F0F4F5', size='12pt')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('bottom').setTextPen('#F0F4F5')
            plot_widget.getAxis('left').setTextPen('#F0F4F5')
            plot_widget.setTitle(title, color='#F0F4F5', size='14pt')
            plot_widget.setXRange(*x_range)

        self.hist_data_all = np.zeros(40)
        self.hist_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_all, width=100, brush='#FF6F61')
        self.hist_plot_all.addItem(self.hist_bar_all)
        configure_histogram_plot(self.hist_plot_all, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_all = []
        bar_centers = np.arange(40)*100 + 50
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_all[i] + 0.5)
            self.hist_plot_all.addItem(label)
            self.hist_labels_all.append(label)

        self.hist2_data_all = np.zeros(40)
        self.hist2_bar_all = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_all, width=100, brush='#FFCA28')
        self.hist2_plot_all.addItem(self.hist2_bar_all)
        configure_histogram_plot(self.hist2_plot_all, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_all = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_all[i] + 0.5)
            self.hist2_plot_all.addItem(label)
            self.hist2_labels_all.append(label)

        self.hist_data_tab = np.zeros(40)
        self.hist_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist_data_tab, width=100, brush='#FF6F61')
        self.hist_plot_tab.addItem(self.hist_bar_tab)
        configure_histogram_plot(self.hist_plot_tab, "Timestamp Histogram (SPD1)", '#FF6F61')
        self.hist_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist_data_tab[i] + 0.5)
            self.hist_plot_tab.addItem(label)
            self.hist_labels_tab.append(label)

        self.hist2_data_tab = np.zeros(40)
        self.hist2_bar_tab = pg.BarGraphItem(x0=np.arange(40)*100, height=self.hist2_data_tab, width=100, brush='#FFCA28')
        self.hist2_plot_tab.addItem(self.hist2_bar_tab)
        configure_histogram_plot(self.hist2_plot_tab, "Timestamp Histogram (SPD2)", '#FFCA28')
        self.hist2_labels_tab = []
        for i in range(40):
            label = pg.TextItem(text="0", color='#F0F4F5', anchor=(0.5, 1.0))
            label.setPos(bar_centers[i], self.hist2_data_tab[i] + 0.5)
            self.hist2_plot_tab.addItem(label)
            self.hist2_labels_tab.append(label)

        self.qber_x_all = []
        self.qber_y_all = []
        self.qber_line_all = self.qber_plot_all.plot(self.qber_x_all, self.qber_y_all, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_all, 'QBER (%)', "Quantum Bit Error Rate")

        self.qber_x_tab = []
        self.qber_y_tab = []
        self.qber_line_tab = self.qber_plot_tab.plot(self.qber_x_tab, self.qber_y_tab, pen=pg.mkPen('#40C4FF', width=2))
        configure_line_plot(self.qber_plot_tab, 'QBER (%)', "Quantum Bit Error Rate")

        self.kbps_x_all = []
        self.kbps_y_all = []
        self.kbps_line_all = self.kbps_plot_all.plot(self.kbps_x_all, self.kbps_y_all, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_all, 'kbps', "Throughput (kbps)")

        self.kbps_x_tab = []
        self.kbps_y_tab = []
        self.kbps_line_tab = self.kbps_plot_tab.plot(self.kbps_x_tab, self.kbps_y_tab, pen=pg.mkPen('#AB47BC', width=2))
        configure_line_plot(self.kbps_plot_tab, 'kbps', "Throughput (kbps)")

        self.visibility_x_all = []
        self.visibility_y_all = []
        self.visibility_line_all = self.visibility_plot_all.plot(self.visibility_x_all, self.visibility_y_all, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_all, 'Ratio', "Visibility Ratio")

        self.visibility_x_tab = []
        self.visibility_y_tab = []
        self.visibility_line_tab = self.visibility_plot_tab.plot(self.visibility_x_tab, self.visibility_y_tab, pen=pg.mkPen('#26A69A', width=2))
        configure_line_plot(self.visibility_plot_tab, 'Ratio', "Visibility Ratio")

        self.spd1_x_all = []
        self.spd1_y_all = []
        self.spd1_line_all = self.spd1_plot_all.plot(self.spd1_x_all, self.spd1_y_all, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_all, 'Value', "SPD1 Decoy Randomness")

        self.spd1_x_tab = []
        self.spd1_y_tab = []
        self.spd1_line_tab = self.spd1_plot_tab.plot(self.spd1_x_tab, self.spd1_y_tab, pen=pg.mkPen('#FF6F61', width=2))
        configure_line_plot(self.spd1_plot_tab, 'Value', "SPD1 Decoy Randomness")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

    def update_plots(self):
        try:
            for _ in range(100):
                data = self.data_queue.get_nowait()
                current_time = time.time() - self.start_time
                logging.debug(f"Processing data: {data}")

                if data['type'] == 'session_number':
                    new_session = data['value']
                    if new_session != self.current_session:
                        # Log missing data types from previous session
                        expected_types = {'timestamp_spd1', 'timestamp_spd2', 'spd1_decaystate', 'visibility', 'qber', 'key', 'kbps_data'}
                        missing_types = expected_types - self.session_data_types
                        if missing_types and self.current_session != -1:
                            logging.warning(f"Session {self.current_session} missing data types: {missing_types}")
                            if 'key' not in self.session_data_types:
                                self.key_display.setText(f"Key ({self.current_session}): Not Available")
                        self.current_session = new_session
                        self.session_data_types = set()
                    continue

                self.session_data_types.add(data['type'])

                if data['type'] == 'timestamp_spd1':
                    timestamp_ps = int(data['value'])
                    logging.debug(f"SPD1 timestamp: {timestamp_ps}")
                    partition1 = min((timestamp_ps // 100) % 40, 39)
                    self.hist_data_all[partition1] += 1
                    self.hist_bar_all.setOpts(height=self.hist_data_all)
                    self.hist_labels_all[partition1].setText(str(int(self.hist_data_all[partition1])))
                    self.hist_labels_all[partition1].setPos(partition1*100 + 50, self.hist_data_all[partition1] + 0.5)
                    self.hist_plot_all.setYRange(0, max(self.hist_data_all.max() * 1.2, 10))
                    logging.debug(f"SPD1 histogram data: {self.hist_data_all}")

                    self.hist_data_tab[partition1] += 1
                    self.hist_bar_tab.setOpts(height=self.hist_data_tab)
                    self.hist_labels_tab[partition1].setText(str(int(self.hist_data_tab[partition1])))
                    self.hist_labels_tab[partition1].setPos(partition1*100 + 50, self.hist_data_tab[partition1] + 0.5)
                    self.hist_plot_tab.setYRange(0, max(self.hist_data_tab.max() * 1.2, 10))
                    logging.debug(f"SPD1 tab histogram data: {self.hist_data_tab}")

                elif data['type'] == 'timestamp_spd2':
                    timestamp_ps = int(data['value'])
                    logging.debug(f"SPD2 timestamp: {timestamp_ps}")
                    partition2 = min((timestamp_ps // 100) % 40, 39)
                    self.hist2_data_all[partition2] += 1
                    self.hist2_bar_all.setOpts(height=self.hist2_data_all)
                    self.hist2_labels_all[partition2].setText(str(int(self.hist2_data_all[partition2])))
                    self.hist2_labels_all[partition2].setPos(partition2*100 + 50, self.hist2_data_all[partition2] + 0.5)
                    self.hist2_plot_all.setYRange(0, max(self.hist2_data_all.max() * 1.2, 10))
                    logging.debug(f"SPD2 histogram data: {self.hist2_data_all}")

                    self.hist2_data_tab[partition2] += 1
                    self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
                    self.hist2_labels_tab[partition2].setText(str(int(self.hist2_data_tab[partition2])))
                    self.hist2_labels_tab[partition2].setPos(partition2*100 + 50, self.hist2_data_tab[partition2] + 0.5)
                    self.hist2_plot_tab.setYRange(0, max(self.hist2_data_tab.max() * 1.2, 10))
                    logging.debug(f"SPD2 tab histogram data: {self.hist2_data_tab}")

                elif data['type'] == 'qber':
                    qber_val = float(data['value'])
                    logging.debug(f"QBER: {qber_val}")
                    self.qber_x_all.append(current_time)
                    self.qber_y_all.append(qber_val)
                    while self.qber_x_all and self.qber_x_all[0] < current_time - 60:
                        self.qber_x_all.pop(0)
                        self.qber_y_all.pop(0)
                    self.qber_line_all.setData(self.qber_x_all, self.qber_y_all)
                    self.qber_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.qber_x_tab.append(current_time)
                    self.qber_y_tab.append(qber_val)
                    while self.qber_x_tab and self.qber_x_tab[0] < current_time - 60:
                        self.qber_x_tab.pop(0)
                        self.qber_y_tab.pop(0)
                    self.qber_line_tab.setData(self.qber_x_tab, self.qber_y_tab)
                    self.qber_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'kbps_data':
                    kbps = float(data['kbps'])
                    logging.debug(f"KBPS: {kbps}")
                    self.kbps_x_all.append(current_time)
                    self.kbps_y_all.append(kbps)
                    while self.kbps_x_all and self.kbps_x_all[0] < current_time - 60:
                        self.kbps_x_all.pop(0)
                        self.kbps_y_all.pop(0)
                    self.kbps_line_all.setData(self.kbps_x_all, self.kbps_y_all)
                    self.kbps_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.kbps_x_tab.append(current_time)
                    self.kbps_y_tab.append(kbps)
                    while self.kbps_x_tab and self.kbps_x_tab[0] < current_time - 60:
                        self.kbps_x_tab.pop(0)
                        self.kbps_y_tab.pop(0)
                    self.kbps_line_tab.setData(self.kbps_x_tab, self.kbps_y_tab)
                    self.kbps_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'key':
                    logging.debug(f"Key: {data['value'][:40]}...")
                    self.key_display.setText(f"Key ({self.current_session}): {data['value']}")

                elif data['type'] == 'visibility':
                    vis_val = float(data['value'])
                    logging.debug(f"Visibility: {vis_val}")
                    self.visibility_x_all.append(current_time)
                    self.visibility_y_all.append(vis_val)
                    while self.visibility_x_all and self.visibility_x_all[0] < current_time - 60:
                        self.visibility_x_all.pop(0)
                        self.visibility_y_all.pop(0)
                    self.visibility_line_all.setData(self.visibility_x_all, self.visibility_y_all)
                    self.visibility_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.visibility_x_tab.append(current_time)
                    self.visibility_y_tab.append(vis_val)
                    while self.visibility_x_tab and self.visibility_x_tab[0] < current_time - 60:
                        self.visibility_x_tab.pop(0)
                        self.visibility_y_tab.pop(0)
                    self.visibility_line_tab.setData(self.visibility_x_tab, self.visibility_y_tab)
                    self.visibility_plot_tab.setXRange(max(0, current_time - 60), current_time)

                elif data['type'] == 'spd1_decaystate':
                    spd1_val = float(data['value'])
                    logging.debug(f"SPD1 Decay: {spd1_val}")
                    self.spd1_x_all.append(current_time)
                    self.spd1_y_all.append(spd1_val)
                    while self.spd1_x_all and self.spd1_x_all[0] < current_time - 60:
                        self.spd1_x_all.pop(0)
                        self.spd1_y_all.pop(0)
                    self.spd1_line_all.setData(self.spd1_x_all, self.spd1_y_all)
                    self.spd1_plot_all.setXRange(max(0, current_time - 60), current_time)

                    self.spd1_x_tab.append(current_time)
                    self.spd1_y_tab.append(spd1_val)
                    while self.spd1_x_tab and self.spd1_x_tab[0] < current_time - 60:
                        self.spd1_x_tab.pop(0)
                        self.spd1_y_tab.pop(0)
                    self.spd1_line_tab.setData(self.spd1_x_tab, self.spd1_y_tab)
                    self.spd1_plot_tab.setXRange(max(0, current_time - 60), current_time)

        except Empty:
            pass

    def start_processor(self):
        logging.info("Starting processor")
        self.processor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_time = time.time()
        self.current_session = -1
        self.session_data_types = set()
        self.key_display.setText(f"Key (None): None")
        # Temporarily disable histogram reset to test data accumulation
        # self.hist_data_all.fill(0)
        # self.hist_data_tab.fill(0)
        # self.hist2_data_all.fill(0)
        # self.hist2_data_tab.fill(0)
        # self.hist_bar_all.setOpts(height=self.hist_data_all)
        # self.hist_bar_tab.setOpts(height=self.hist_data_tab)
        # self.hist2_bar_all.setOpts(height=self.hist2_data_all)
        # self.hist2_bar_tab.setOpts(height=self.hist2_data_tab)
        # for i in range(40):
        #     self.hist_labels_all[i].setText("0")
        #     self.hist_labels_all[i].setPos(i*100 + 50, 0.5)
        #     self.hist_labels_tab[i].setText("0")
        #     self.hist_labels_tab[i].setPos(i*100 + 50, 0.5)
        #     self.hist2_labels_all[i].setText("0")
        #     self.hist2_labels_all[i].setPos(i*100 + 50, 0.5)
        #     self.hist2_labels_tab[i].setText("0")
        #     self.hist2_labels_tab[i].setPos(i*100 + 50, 0.5)

    def stop_processor(self):
        logging.info("Stopping processor")
        self.processor.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        logging.info("Closing window")
        self.processor.close()
        self.marquee_timer.stop()
        event.accept()