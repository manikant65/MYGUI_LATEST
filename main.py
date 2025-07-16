'''import sys
from queue import Queue
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from data_processor import DataProcessor

def main():
    mode = "file"  # Default to file mode
    if len(sys.argv) > 1 and sys.argv[1] in ["console", "file"]:
        mode = sys.argv[1]
    
    data_queue = Queue()
    processor = DataProcessor(data_queue, mode=mode)
    app = QApplication(sys.argv)
    window = MainWindow(data_queue, processor)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()'''
    
    
    
    
    
import sys
from queue import Queue
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from data_processor import DataProcessor

def main():
    mode = "file"  # Default to file mode
    if len(sys.argv) > 1 and sys.argv[1] in ["console", "file"]:
        mode = sys.argv[1]
    
    data_queue = Queue()
    processor = DataProcessor(data_queue, mode=mode, input_string="default_input")
    app = QApplication(sys.argv)
    window = MainWindow(data_queue, processor)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()





"""

'''
import os
import matplotlib.pyplot as plt

#Path components
folder_path = "C:/Users/YourName/Documents/data"  # Change this to your folder
file_name = "values.txt"                          # Your file name

# Construct full file path
file_path = os.path.join(folder_path, file_name)

#Parameters
divisor = 10
modulo = 10000
bins = 100

# Read and process values
processed_values = [10,20,30,40,50,60,70,80,90,11,23,12,13,130,250]

with open(file_path, 'r') as file:
    for line in file:
        line = line.strip()
        if line.isdigit():
            num = int(line)
            processed = (num // divisor) % modulo
            processed_values.append(processed)

# Plot histogram
plt.hist(processed_values, bins=bins, range=(0, 10000), color='skyblue', edgecolor='black')
plt.title('Histogram of Processed 12-digit Numbers')
plt.xlabel('Value Range')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()'''




import os
import matplotlib.pyplot as plt

# Path components
#folder_path = "C:/Users/YourName/Documents/data"  # Replace 'YourName' with actual username
#file_name = "values.txt"                          # Your file name
#file_path = os.path.join(folder_path, file_name)

# Parameters
divisor = 10
modulo = 10000
bins = 20  # Reduced bins to better suit small dataset

# Read and process values
processed_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 11, 23, 12, 13, 130, 250]  # Fallback data
'''
# Read from file if it exists
if os.path.exists(file_path):
    processed_values = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.isdigit():  # Check if line is a valid integer
                num = int(line)
                processed = (num // divisor) % modulo
                processed_values.append(processed)

# Validate processed_values
if not processed_values:
    print("No valid data to plot.")
    exit()'''

# Adjust range dynamically based on data
data_min = min(processed_values)
data_max = max(processed_values)
range_margin = (data_max - data_min) * 0.1  # Add 10% margin for better visualization
plot_range = (max(0, data_min - range_margin), data_max + range_margin)

# Plot histogram
plt.figure(figsize=(10, 6))  # Set figure size for better readability
plt.hist(processed_values, bins=bins, range=plot_range, color='skyblue', edgecolor='black')
plt.title('Histogram of Processed Numbers')
plt.xlabel('Value Range')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)  # Lighter grid for better visibility
plt.tight_layout()  # Adjust layout to prevent label cutoff

# Save plot to file (optional, uncomment if needed)
# plt.savefig('histogram.png', dpi=300)

plt.show()"""

