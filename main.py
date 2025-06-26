import sys
from queue import Queue
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from data_processor import DataProcessor

def main():
    data_queue = Queue()
    processor = DataProcessor(data_queue)
    app = QApplication(sys.argv)
    window = MainWindow(data_queue, processor)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()