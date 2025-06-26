Quantum Key Distribution Output Analyzer
Overview
This project implements a Quantum Key Distribution (QKD) Output Analyzer, a system to simulate and visualize QKD data in real-time. The application generates simulated QKD metrics such as timestamps (for histograms), Quantum Bit Error Rate (QBER), throughput, visibility ratio, and SPD1 decoy randomness, and displays them using a graphical user interface (GUI) built with PyQt6 and pyqtgraph.
The system consists of four main components:

A C program (c_program.c) that generates simulated QKD data.
A Python data processor (data_processor.py) that reads the C program's output and queues the data.
A Python GUI (gui.py) that visualizes the data as histograms and moving line graphs.
A Python main script (main.py) that ties everything together and launches the application.

Features

Histograms: Displays timestamp histograms for SPD1 and SPD2, updated every 100ms.
Moving Line Graphs: Plots QBER, throughput, visibility ratio, and SPD1 decoy randomness as moving line graphs with time on the X-axis.
Real-Time Updates: Data is generated every 100ms, followed by a 10ms sleep, with the data queue cleared after each cycle.
Interactive GUI: Includes a tabbed interface with an "All" tab showing all plots, plus dedicated tabs for each metric (Histogram SPD1, Histogram SPD2, QBER, Throughput, Visibility, SPD1 Decoy Randomness).
Control Buttons: Start and Stop buttons to control data processing, plus a marquee and key display.

Folder Structure
The project is organized as follows:
C:\Users\MANIKANT\Desktop\MY GUI\
├── src/
│   ├── c_program.c           # C program to generate simulated QKD data
│   ├── data_processor.py     # Python script to process C program output and queue data
│   ├── gui.py                # Python script for the GUI to visualize data
│   └── main.py               # Entry point to launch the application
├── build/
│   └── c_program.exe         # Compiled C program executable
└── README.md                 # Project documentation (this file)

File Descriptions

src/c_program.c:

Generates simulated QKD data every 100ms, including:
TIMESTAMP: Integer (0-9999) for histograms.
QBER: Float (0.0-9.99) for Quantum Bit Error Rate.
KBPS: Float (0.0-9.99) for throughput.
VISIBILITY: Float (0.0-0.99) for visibility ratio.
SPD1_DECAYSTATE: Float (0.0-9.99) for SPD1 decoy randomness.
KEY: 128-bit key as 32 hexadecimal characters.


Sleeps for 10ms after each 100ms data generation cycle.
Outputs data to stdout in the format TYPE,value.


src/data_processor.py:

Runs c_program.exe as a subprocess.
Reads the C program's output, parses it, and places the data into a thread-safe queue.
Manages the 100ms data generation cycle, sleeping for 10ms and clearing the queue after each cycle.
Provides methods to start, stop, and close the subprocess.


src/gui.py:

Implements the GUI using PyQt6 and pyqtgraph.
Displays two histograms (SPD1 and SPD2) and four moving line graphs (QBER, Throughput, Visibility, SPD1 Decoy Randomness).
Updates plots in real-time by consuming data from the queue.
Features a tabbed interface, a marquee, a key display, and Start/Stop buttons.


src/main.py:

The entry point of the application.
Initializes the data queue, data processor, and GUI.
Launches the PyQt6 application event loop.



Prerequisites
Before building and running the project, ensure you have the following installed:

Python 3.8+:

Install Python from python.org.
Verify installation:python --version




Python Dependencies:

Install required packages using pip:pip install pyqt6 pyqtgraph numpy




C Compiler (e.g., GCC):

Windows: Install MinGW or MSYS2. For MinGW, download from mingw-w64.org and add to PATH.
Linux/macOS: GCC is typically pre-installed. If not, install it:
Ubuntu: sudo apt-get install gcc
macOS: Install Xcode Command Line Tools (xcode-select --install).


Verify installation:gcc --version





Build Instructions

Clone or Set Up the Project:

Ensure all files (c_program.c, data_processor.py, gui.py, main.py) are in the src/ directory.
Create the build/ directory if it doesn’t exist:mkdir build




Compile the C Program:

Open a terminal in C:\Users\MANIKANT\Desktop\MY GUI.
Compile c_program.c to create the executable in the build/ directory:gcc src/c_program.c -o build/c_program.exe


Note for Linux/macOS: Omit the .exe extension:gcc src/c_program.c -o build/c_program


Verify the executable exists in build/.


Verify Folder Structure:

Ensure the structure matches the one described above.
The compiled executable should be at build/c_program.exe (or build/c_program on Linux/macOS).



Run Instructions

Navigate to Project Directory:

Open a terminal in C:\Users\MANIKANT\Desktop\MY GUI.


Run the Application:

Execute the main script:python src/main.py


The GUI should launch, displaying the QKD Output Analyzer.


Interact with the GUI:

Start Button: Click to begin data generation and plotting.
Stop Button: Click to pause data processing.
Tabs:
"All": Shows all plots (two histograms and four line graphs).
"Histogram (SPD1)" and "Histogram (SPD2)": Dedicated timestamp histograms.
"QBER", "Throughput", "Visibility", "SPD1 Decoy Randomness": Dedicated line graphs.


Marquee: A scrolling text at the top.
Key Display: Shows the latest 128-bit key.
Close the window to exit the application.



Expected Behavior

Histograms: SPD1 and SPD2 histograms update every 100ms with timestamp data.
Line Graphs: QBER, throughput, visibility, and SPD1 decoy randomness are plotted as moving line graphs, showing the last 60 seconds of data.
Timing: Data is generated every 100ms, followed by a 10ms sleep, with the queue cleared after each cycle.
GUI Updates: Plots update smoothly in real-time, reflecting the simulated QKD data.

Troubleshooting

C Program Not Found:

Ensure build/c_program.exe exists. Recompile if necessary:gcc src/c_program.c -o build/c_program.exe


Verify the path in data_processor.py:self.c_program_path = os.path.join("build", "c_program.exe")




Plots Not Updating:

Run the C program manually to check its output:.\build\c_program.exe


It should output lines like TIMESTAMP,<int>, QBER,<float>, etc.
Add debug prints in data_processor.py to verify data parsing:print(f"Parsed data: {data_type}, {value}")




GUI Freezing:

Ensure the timer interval in gui.py is not too short. It’s set to 10ms:self.timer.setInterval(10)


If freezing persists, increase to 20ms:self.timer.setInterval(20)




Dependency Errors:

Verify all Python packages are installed:pip install pyqt6 pyqtgraph numpy





License
This project is for educational purposes and has no specific license. Use and modify as needed for learning and experimentation.

Generated on June 17, 2025
