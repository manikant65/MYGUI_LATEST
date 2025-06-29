'''
import subprocess
import os
from queue import Queue, Empty
import threading
import time

class DataProcessor:
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.process = None
        self.running = False
        self.thread = None
        # Path to the compiled C program
        self.c_program_path = os.path.join("build", "c_program.exe")

    def start(self):
        if not self.running:
            # Start the C program as a subprocess
            self.process = subprocess.Popen(
                self.c_program_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            self.running = True
            # Start a thread to read the output
            self.thread = threading.Thread(target=self.read_output)
            self.thread.daemon = True
            self.thread.start()

    def read_output(self):
        while self.running:
            # Read data for the 100ms period
            start_time = time.time()
            while time.time() - start_time < 0.1:  # 100ms window
                line = self.process.stdout.readline().strip()
                if not line and self.process.poll() is not None:
                    self.running = False
                    break
                if line:
                    self.parse_and_queue(line)

            # After 100ms, sleep for 10ms and clear the queue
            time.sleep(0.01)  # 10ms sleep
            # Clear the queue
            while True:
                try:
                    self.data_queue.get_nowait()
                except Empty:
                    break

    def parse_and_queue(self, line: str):
        try:
            # Expected format: TYPE,value
            parts = line.split(',')
            if len(parts) < 2:
                return
            data_type = parts[0].strip()
            value = ','.join(parts[1:]).strip()  # Handle values that might contain commas

            if data_type == "TIMESTAMP":
                self.data_queue.put({"type": "timestamp", "value": int(value)})
            elif data_type == "QBER":
                self.data_queue.put({"type": "qber", "value": float(value)})
            elif data_type == "KBPS":
                self.data_queue.put({"type": "kbps_data", "kbps": float(value)})
            elif data_type == "KEY":
                self.data_queue.put({"type": "key", "value": value})
            elif data_type == "VISIBILITY":
                self.data_queue.put({"type": "visibility", "value": float(value)})
            elif data_type == "SPD1_DECAYSTATE":
                self.data_queue.put({"type": "spd1_decaystate", "value": float(value)})
        except (ValueError, IndexError) as e:
            print(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            self.running = False
            if self.process:
                self.process.terminate()
                self.process.wait()
            if self.thread:
                self.thread.join()

    def close(self):
        self.stop()
        if self.process:
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None   '''
            
'''          
import subprocess
import os
from queue import Queue, Empty
import threading
import time

class DataProcessor:
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.process = None
        self.running = False
        self.thread = None
        # Path to the compiled C program
        self.c_program_path = os.path.join("build", "c_program.exe")

    def start(self):
        if not self.running:
            # Start the C program as a subprocess
            self.process = subprocess.Popen(
                self.c_program_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            self.running = True
            # Start a thread to read the output
            self.thread = threading.Thread(target=self.read_output)
            self.thread.daemon = True
            self.thread.start()

    def read_output(self):
        while self.running:
            # Read data for the 100ms period
            start_time = time.time()
            while time.time() - start_time < 0.1:  # 100ms window
                line = self.process.stdout.readline().strip()
                if not line and self.process.poll() is not None:
                    self.running = False
                    break
                if line:
                    self.parse_and_queue(line)

            # After 100ms, sleep for 10ms and clear the queue
            time.sleep(0.01)  # 10ms sleep
            # Clear the queue
            while True:
                try:
                    self.data_queue.get_nowait()
                except Empty:
                    break

    def parse_and_queue(self, line: str):
        try:
            # Expected format: TYPE,value
            parts = line.split(',')
            if len(parts) < 2:
                return
            data_type = parts[0].strip()
            value = ','.join(parts[1:]).strip()  # Handle values that might contain commas

            if data_type == "TIMESTAMP_SPD1":
                self.data_queue.put({"type": "timestamp_spd1", "value": int(value)})
            elif data_type == "TIMESTAMP_SPD2":
                self.data_queue.put({"type": "timestamp_spd2", "value": int(value)})
            elif data_type == "QBER":
                self.data_queue.put({"type": "qber", "value": float(value)})
            elif data_type == "KBPS":
                self.data_queue.put({"type": "kbps_data", "kbps": float(value)})
            elif data_type == "KEY":
                self.data_queue.put({"type": "key", "value": value})
            elif data_type == "VISIBILITY":
                self.data_queue.put({"type": "visibility", "value": float(value)})
            elif data_type == "SPD1_DECAYSTATE":
                self.data_queue.put({"type": "spd1_decaystate", "value": float(value)})
        except (ValueError, IndexError) as e:
            print(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            self.running = False
            if self.process:
                self.process.terminate()
                self.process.wait()
            if self.thread:
                self.thread.join()

    def close(self):
        self.stop()
        if self.process:
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None'''
            
'''          
import subprocess
import os
from queue import Queue, Empty
import threading

class DataProcessor:
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.process = None
        self.running = False
        self.thread = None
        # Path to the compiled C program
        self.c_program_path = os.path.join("build", "c_program.exe")

    def start(self):
        if not self.running:
            # Start the C program as a subprocess
            self.process = subprocess.Popen(
                self.c_program_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            self.running = True
            # Start a thread to read the output
            self.thread = threading.Thread(target=self.read_output)
            self.thread.daemon = True
            self.thread.start()

    def read_output(self):
        while self.running:
            line = self.process.stdout.readline().strip()
            if not line and self.process.poll() is not None:
                self.running = False
                break
            if line:
                self.parse_and_queue(line)

    def parse_and_queue(self, line: str):
        try:
            # Expected format: TYPE,value
            parts = line.split(',')
            if len(parts) < 2:
                return
            data_type = parts[0].strip()
            value = ','.join(parts[1:]).strip()  # Handle values that might contain commas

            if data_type == "TIMESTAMP_SPD1":
                self.data_queue.put({"type": "timestamp_spd1", "value": int(value)})
            elif data_type == "TIMESTAMP_SPD2":
                self.data_queue.put({"type": "timestamp_spd2", "value": int(value)})
            elif data_type == "QBER":
                self.data_queue.put({"type": "qber", "value": float(value)})
            elif data_type == "KBPS":
                self.data_queue.put({"type": "kbps_data", "kbps": float(value)})
            elif data_type == "KEY":
                self.data_queue.put({"type": "key", "value": value})
            elif data_type == "VISIBILITY":
                self.data_queue.put({"type": "visibility", "value": float(value)})
            elif data_type == "SPD1_DECAYSTATE":
                self.data_queue.put({"type": "spd1_decaystate", "value": float(value)})
        except (ValueError, IndexError) as e:
            print(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            self.running = False
            if self.process:
                self.process.terminate()
                self.process.wait()
            if self.thread:
                self.thread.join()

    def close(self):
        self.stop()
        if self.process:
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None'''
            
            


'''
import subprocess
import os
from queue import Queue, Empty
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.process = None
        self.running = False
        self.thread = None
        self.spd1_values_mode = False
        self.spd2_values_mode = False
        self.spd1_count = 0
        self.spd2_count = 0
        self.c_program_path = os.path.join("build", "c_program.exe")

    def start(self):
        if not self.running:
            logging.info("Starting data processor")
            try:
                self.process = subprocess.Popen(
                    self.c_program_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                self.running = True
                self.thread = threading.Thread(target=self.read_output)
                self.thread.daemon = True
                self.thread.start()
            except Exception as e:
                logging.error(f"Failed to start subprocess: {e}")

    def read_output(self):
        while self.running:
            line = self.process.stdout.readline().strip()
            if not line and self.process.poll() is not None:
                logging.info("Subprocess terminated")
                self.running = False
                break
            if line:
                logging.debug(f"Read line: {line}")
                self.parse_and_queue(line)

    def parse_and_queue(self, line: str):
        try:
            if line == "SPD1_VALUES:":
                logging.info("Entering SPD1_VALUES mode")
                self.spd1_values_mode = True
                self.spd2_values_mode = False
                self.spd1_count = 0
                return
            elif line == "SPD2_VALUES:":
                logging.info("Entering SPD2_VALUES mode")
                self.spd1_values_mode = False
                self.spd2_values_mode = True
                self.spd2_count = 0
                return
            elif line.startswith("SESSION_NUMBER:") or line.startswith("NUMBER_OF_RX_KEY_BITS"):
                logging.debug(f"Ignoring line: {line}")
                return

            if self.spd1_values_mode and self.spd1_count < 40:
                try:
                    value = int(line)
                    self.data_queue.put({"type": "timestamp_spd1", "value": value})
                    logging.debug(f"Queued SPD1 timestamp: {value}")
                    self.spd1_count += 1
                    return
                except ValueError:
                    logging.warning(f"Invalid SPD1 value: {line}")
                    return
            elif self.spd2_values_mode and self.spd2_count < 40:
                try:
                    value = int(line)
                    self.data_queue.put({"type": "timestamp_spd2", "value": value})
                    logging.debug(f"Queued SPD2 timestamp: {value}")
                    self.spd2_count += 1
                    return
                except ValueError:
                    logging.warning(f"Invalid SPD2 value: {line}")
                    return

            parts = line.split(':', 1) if ':' in line else [line, '']
            if len(parts) < 2:
                logging.debug(f"Skipping invalid line: {line}")
                return

            data_type = parts[0].strip()
            value = parts[1].strip()

            if data_type == "DECOY_STATE_RANDOMNESS_AT_SPD1":
                self.data_queue.put({"type": "spd1_decaystate", "value": float(value)})
                logging.debug(f"Queued spd1_decaystate: {value}")
            elif data_type == "VISIBILITY_RATIO_IS":
                self.data_queue.put({"type": "visibility", "value": float(value)})
                logging.debug(f"Queued visibility: {value}")
            elif data_type == "SPD1_QBER_VALUE_IS":
                self.data_queue.put({"type": "qber", "value": float(value)})
                logging.debug(f"Queued qber: {value}")
            elif data_type == "KEY_BITS":
                self.data_queue.put({"type": "key", "value": value})
                logging.debug(f"Queued key: {value[:40]}...")
            elif data_type == "KEY_RATE_PER_SECOND_IS":
                self.data_queue.put({"type": "kbps_data", "kbps": float(value)})
                logging.debug(f"Queued kbps: {value}")

        except Exception as e:
            logging.error(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            logging.info("Stopping data processor")
            self.running = False
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            if self.thread:
                self.thread.join()

    def close(self):
        self.stop()
        if self.process:
            logging.info("Closing data processor")
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None'''
            
            

'''

import subprocess
import os
from queue import Queue, Empty
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.process = None
        self.running = False
        self.thread = None
        self.spd1_values_mode = False
        self.spd2_values_mode = False
        self.spd1_count = 0
        self.spd2_count = 0
        self.session_data_types = set()
        self.current_session = -1
        self.c_program_path = os.path.join("build", "c_program.exe")

    def start(self):
        if not self.running:
            logging.info("Starting data processor")
            try:
                self.process = subprocess.Popen(
                    self.c_program_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                self.running = True
                self.thread = threading.Thread(target=self.read_output)
                self.thread.daemon = True
                self.thread.start()
            except Exception as e:
                logging.error(f"Failed to start subprocess: {e}")

    def read_output(self):
        while self.running:
            line = self.process.stdout.readline().strip()
            if not line and self.process.poll() is not None:
                logging.info("Subprocess terminated")
                self.running = False
                break
            if line:
                logging.debug(f"Read line: {line}")
                self.parse_and_queue(line)

    def parse_and_queue(self, line: str):
        try:
            if line.startswith("SESSION_NUMBER:"):
                new_session = int(line.split(':')[1])
                if new_session != self.current_session:
                    # Log missing data types from previous session
                    expected_types = {'timestamp_spd1', 'timestamp_spd2', 'spd1_decaystate', 'visibility', 'qber', 'key', 'kbps_data'}
                    missing_types = expected_types - self.session_data_types
                    if missing_types and self.current_session != -1:
                        logging.warning(f"Session {self.current_session} missing data types: {missing_types}")
                    self.current_session = new_session
                    self.session_data_types = set()
                    self.data_queue.put({"type": "session_number", "value": new_session})
                    logging.debug(f"Queued session_number: {new_session}")
                return

            if line == "SPD1_VALUES:":
                logging.info("Entering SPD1_VALUES mode")
                self.spd1_values_mode = True
                self.spd2_values_mode = False
                self.spd1_count = 0
                return
            elif line == "SPD2_VALUES:":
                logging.info("Entering SPD2_VALUES mode")
                self.spd1_values_mode = False
                self.spd2_values_mode = True
                self.spd2_count = 0
                return
            elif line.startswith("NUMBER_OF_RX_KEY_BITS"):
                logging.debug(f"Ignoring line: {line}")
                return

            if self.spd1_values_mode and self.spd1_count < 40:
                try:
                    value = int(line)
                    self.data_queue.put({"type": "timestamp_spd1", "value": value})
                    self.session_data_types.add("timestamp_spd1")
                    self.spd1_count += 1
                    logging.debug(f"Queued SPD1 timestamp {self.spd1_count}/40: {value}")
                    if self.spd1_count == 40:
                        logging.info(f"Completed queuing 40 SPD1 timestamps for session {self.current_session}")
                    return
                except ValueError:
                    logging.warning(f"Invalid SPD1 value: {line}")
                    return
            elif self.spd2_values_mode and self.spd2_count < 40:
                try:
                    value = int(line)
                    self.data_queue.put({"type": "timestamp_spd2", "value": value})
                    self.session_data_types.add("timestamp_spd2")
                    self.spd2_count += 1
                    logging.debug(f"Queued SPD2 timestamp {self.spd2_count}/40: {value}")
                    if self.spd2_count == 40:
                        logging.info(f"Completed queuing 40 SPD2 timestamps for session {self.current_session}")
                    return
                except ValueError:
                    logging.warning(f"Invalid SPD2 value: {line}")
                    return

            parts = line.split(':', 1) if ':' in line else [line, '']
            if len(parts) < 2:
                logging.debug(f"Skipping invalid line: {line}")
                return

            data_type = parts[0].strip()
            value = parts[1].strip()

            if data_type == "DECOY_STATE_RANDOMNESS_AT_SPD1":
                self.data_queue.put({"type": "spd1_decaystate", "value": float(value)})
                self.session_data_types.add("spd1_decaystate")
                logging.debug(f"Queued spd1_decaystate: {value}")
            elif data_type == "VISIBILITY_RATIO_IS":
                self.data_queue.put({"type": "visibility", "value": float(value)})
                self.session_data_types.add("visibility")
                logging.debug(f"Queued visibility: {value}")
            elif data_type == "SPD1_QBER_VALUE_IS":
                self.data_queue.put({"type": "qber", "value": float(value)})
                self.session_data_types.add("qber")
                logging.debug(f"Queued qber: {value}")
            elif data_type == "KEY_BITS":
                self.data_queue.put({"type": "key", "value": value})
                self.session_data_types.add("key")
                logging.debug(f"Queued key: {value[:40]}...")
            elif data_type == "KEY_RATE_PER_SECOND_IS":
                self.data_queue.put({"type": "kbps_data", "kbps": float(value)})
                self.session_data_types.add("kbps_data")
                logging.debug(f"Queued kbps: {value}")

        except Exception as e:
            logging.error(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            logging.info("Stopping data processor")
            self.running = False
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            if self.thread:
                self.thread.join()

    def close(self):
        self.stop()
        if self.process:
            logging.info("Closing data processor")
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None'''


#BELOW CODE HANDLES VARIABLE KEY SIZE
import subprocess
import os
from queue import Queue
import threading
import logging
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self, data_queue: Queue, mode: str = "file", file_position: int = 0):
        self.data_queue = data_queue
        self.mode = mode
        self.process = None
        self.file = None
        self.running = False
        self.stop_event = threading.Event()
        self.thread = None
        self.spd1_values_mode = False
        self.spd2_values_mode = False
        self.spd1_count = 0
        self.spd2_count = 0
        self.session_data_types = set()
        self.current_session = -1
        self.file_position = file_position
        self.c_program_path = os.path.join("build", "c_program.exe")
        self.output_file_path = os.path.join("build", "output.txt")

    def start(self):
        if not self.running:
            logging.info(f"Starting data processor in {self.mode} mode")
            self.running = True
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.read_output)
            self.thread.daemon = True
            self.thread.start()

    def read_output(self):
        if self.mode == "console":
            try:
                self.process = subprocess.Popen(
                    self.c_program_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                while self.running and not self.stop_event.is_set():
                    line = self.process.stdout.readline().strip()
                    if not line and self.process.poll() is not None:
                        logging.info("Subprocess terminated")
                        self.running = False
                        break
                    if line:
                        logging.debug(f"Read line from console: {line}")
                        self.parse_and_queue(line)
            except Exception as e:
                logging.error(f"Failed to start subprocess: {e}")
                self.running = False

        elif self.mode == "file":
            try:
                self.file = open(self.output_file_path, "r")
                logging.debug(f"Opened file at position {self.file_position}")
                if self.file_position > 0:
                    self.file.seek(self.file_position)
                    logging.debug(f"Seeking to file position {self.file_position}")
                while self.running and not self.stop_event.is_set():
                    line = self.file.readline().strip()
                    if not line:
                        if self.stop_event.is_set():
                            break
                        import time
                        time.sleep(0.5)
                        continue
                    logging.debug(f"Read line from file: {line}")
                    self.parse_and_queue(line)
            except Exception as e:
                logging.error(f"Failed to read file: {e}")
                self.running = False
            finally:
                if self.file and not self.file.closed:
                    self.file.close()
                    self.file = None

    def parse_and_queue(self, line: str):
        try:
            if self.stop_event.is_set() and self.mode == "file" and self.file and not self.file.closed:
                self.file_position = self.file.tell()
                logging.debug(f"Stopped at file position {self.file_position}")
                self.file.close()
                self.file = None
                return

            if line.startswith("SESSION_NUMBER:"):
                new_session = int(line.split(':')[1])
                if new_session != self.current_session:
                    expected_types = {'timestamp_spd1', 'timestamp_spd2', 'spd1_decaystate', 'visibility', 'qber'}
                    if new_session % 2 == 0:
                        expected_types.add('key')
                    else:
                        expected_types.add('kbps_data')
                    missing_types = expected_types - self.session_data_types
                    if missing_types and self.current_session != -1:
                        logging.warning(f"Session {self.current_session} missing data types: {missing_types}")
                    self.current_session = new_session
                    self.spd1_values_mode = False
                    self.spd2_values_mode = False
                    self.spd1_count = 0
                    self.spd2_count = 0
                    self.session_data_types = set()
                    self.data_queue.put({"type": "session_number", "value": new_session})
                logging.debug(f"Current file position after session: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line == "SPD1_VALUES:":
                self.spd1_values_mode = True
                self.spd2_values_mode = False
                self.spd1_count = 0
                logging.debug(f"Current file position after SPD1_VALUES: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line == "SPD2_VALUES:":
                self.spd1_values_mode = False
                self.spd2_values_mode = True
                self.spd2_count = 0
                logging.debug(f"Current file position after SPD2_VALUES: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if self.spd1_values_mode and self.spd1_count < 40:
                timestamp = int(line)
                self.data_queue.put({"type": "timestamp_spd1", "value": timestamp})
                self.spd1_count += 1
                self.session_data_types.add("timestamp_spd1")
                if self.spd1_count == 40:
                    logging.info(f"Completed queuing 40 SPD1 timestamps for session {self.current_session}")
                logging.debug(f"Current file position after SPD1: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if self.spd2_values_mode and self.spd2_count < 40:
                timestamp = int(line)
                self.data_queue.put({"type": "timestamp_spd2", "value": timestamp})
                self.spd2_count += 1
                self.session_data_types.add("timestamp_spd2")
                if self.spd2_count == 40:
                    logging.info(f"Completed queuing 40 SPD2 timestamps for session {self.current_session}")
                logging.debug(f"Current file position after SPD2: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("DECOY_STATE_RANDOMNESS_AT_SPD1:"):
                value = float(line.split(':')[1])
                self.data_queue.put({"type": "spd1_decaystate", "value": value})
                self.session_data_types.add("spd1_decaystate")
                logging.debug(f"Current file position after spd1_decaystate: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("VISIBILITY_RATIO_IS:"):
                value = float(line.split(':')[1])
                self.data_queue.put({"type": "visibility", "value": value})
                self.session_data_types.add("visibility")
                logging.debug(f"Current file position after visibility: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("SPD1_QBER_VALUE_IS:"):
                value = float(line.split(':')[1])
                self.data_queue.put({"type": "qber", "value": value})
                self.session_data_types.add("qber")
                logging.debug(f"Current file position after qber: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("NUMBER_OF_RX_KEY_BITS_AFTER_PRIVACY_AMPLIFICATION_IS:"):
                logging.debug(f"Current file position after key_bits_length: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("KEY_BITS:"):
                key_match = re.match(r"KEY_BITS:([01]{128,})", line)
                if key_match:
                    key = key_match.group(1)
                    self.data_queue.put({"type": "key", "value": key, "length": len(key)})
                    self.session_data_types.add("key")
                    logging.debug(f"Queued key (length {len(key)}): {key[:40]}... for session {self.current_session}")
                    logging.debug(f"Current file position after key: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                else:
                    logging.error(f"Invalid key format: {line}")
                return

            if line.startswith("KEY_RATE_PER_SECOND_IS:"):
                kbps = float(line.split(':')[1])
                self.data_queue.put({"type": "kbps_data", "kbps": kbps})
                self.session_data_types.add("kbps_data")
                logging.debug(f"Queued kbps: {kbps} for session {self.current_session}")
                logging.debug(f"Current file position after kbps: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

        except Exception as e:
            logging.error(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            logging.info("Stopping data processor")
            self.running = False
            self.stop_event.set()
            if self.mode == "console" and self.process:
                self.process.kill()
                self.process = None
            elif self.mode == "file" and self.file and not self.file.closed:
                self.file_position = self.file.tell()
                logging.debug(f"Saved file position: {self.file_position}")
                self.file.close()
                self.file = None
            if self.thread:
                self.thread.join(timeout=0.1)
                self.thread = None

    def close(self):
        self.stop()
        if self.mode == "console" and self.process:
            logging.info("Closing data processor")
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None

    def get_file_position(self):
        return self.file_position
