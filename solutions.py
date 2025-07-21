import subprocess
import os
from queue import Queue
import threading
import logging
import re
import time
import select
import sys
import asyncio
from multiprocessing import Process, Queue as MPQueue

# Optional imports with fallback
try:
    import pexpect
    PEXPECT_AVAILABLE = True
except ImportError:
    PEXPECT_AVAILABLE = False
    logging.warning("pexpect not available. Some solutions will be disabled.")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self, data_queue: Queue, mode: str = "file", file_position: int = 0, input_string: str = None, 
                 console_read_method: str = "buffer"):
        """
        Enhanced DataProcessor with multiple console reading methods
        
        Args:
            data_queue: Queue for processed data
            mode: "file" or "console"
            file_position: Starting position for file reading
            input_string: Input string for console mode
            console_read_method: Method for console reading:
                - "buffer": Buffered reading (default)
                - "pexpect": Using pexpect library (Unix/Linux only)
                - "delayed": Delayed line processing
                - "async": Asyncio-based reading
                - "multiprocess": Separate process reading
                - "file_tail": Force file output and tail
        """
        self.data_queue = data_queue
        self.mode = mode
        self.input_string = input_string
        self.console_read_method = console_read_method
        self.process = None
        self.file = None
        self.running = False
        self.stop_event = threading.Event()
        self.thread = None
        
        # Console reading specific attributes
        self.console_buffer = ""
        self.pending_lines = {}
        self.line_timers = {}
        self.line_counter = 0
        self.mp_queue = None
        self.reader_process = None
        self.queue_monitor_thread = None
        self.loop = None
        self.temp_output_file = os.path.join("build", "realtime_output.txt")
        
        # Original attributes
        self.spd1_values_mode = False
        self.spd2_values_mode = False
        self.spd1_count = 0
        self.spd2_count = 0
        self.session_data_types = set()
        self.current_session = -1
        self.file_position = file_position
        self.c_program_path = os.path.join("build", "c_program.exe")
        self.output_file_path = os.path.join("build", "output.txt")
        self.last_session_data = {
            "timestamp_spd1": [],
            "timestamp_spd2": [],
            "spd1_decaystate": None,
            "visibility": None,
            "qber": None,
            "key": None,
            "kbps_data": None,
            "input_string": None
        }

    def start(self):
        if not self.running:
            logging.info(f"Starting data processor in {self.mode} mode" + 
                        (f" with input string: {self.input_string}" if self.input_string else "") +
                        (f" using console method: {self.console_read_method}" if self.mode == "console" else ""))
            self.running = True
            self.stop_event.clear()
            
            if self.mode == "console":
                self._start_console_reader()
            else:
                self.thread = threading.Thread(target=self.read_output)
                self.thread.daemon = True
                self.thread.start()

    def _start_console_reader(self):
        """Start appropriate console reader based on method"""
        if self.console_read_method == "buffer":
            self.thread = threading.Thread(target=self._read_console_buffered)
        elif self.console_read_method == "pexpect" and PEXPECT_AVAILABLE:
            self.thread = threading.Thread(target=self._read_console_pexpect)
        elif self.console_read_method == "delayed":
            self.thread = threading.Thread(target=self._read_console_delayed)
        elif self.console_read_method == "async":
            self.thread = threading.Thread(target=self._start_async_reader)
        elif self.console_read_method == "multiprocess":
            self._start_multiprocess_reader()
            return
        elif self.console_read_method == "file_tail":
            self.thread = threading.Thread(target=self._read_file_tail)
        else:
            logging.warning(f"Unknown console read method: {self.console_read_method}. Using buffer method.")
            self.thread = threading.Thread(target=self._read_console_buffered)
        
        if self.thread:
            self.thread.daemon = True
            self.thread.start()

    def read_output(self):
        """Original file reading method"""
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
                    time.sleep(0.1)
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

    def _read_console_buffered(self):
        """Method 1: Buffered console reading"""
        try:
            cmd = [self.c_program_path]
            if self.input_string:
                cmd.append(self.input_string)
            else:
                cmd.append("default_input")
                
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                universal_newlines=True
            )
            
            while self.running and not self.stop_event.is_set():
                try:
                    if self.process.poll() is not None:
                        logging.info("Subprocess terminated")
                        break
                    
                    # Read available data
                    if sys.platform.startswith('win'):
                        try:
                            chunk = self.process.stdout.read(1024)
                            if not chunk:
                                time.sleep(0.01)
                                continue
                        except:
                            time.sleep(0.01)
                            continue
                    else:
                        ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                        if not ready:
                            continue
                        chunk = self.process.stdout.read(1024)
                        if not chunk:
                            continue
                    
                    self.console_buffer += chunk
                    
                    # Process complete lines
                    while '\n' in self.console_buffer:
                        line, self.console_buffer = self.console_buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            logging.debug(f"Buffered read: {line}")
                            self.parse_and_queue(line)
                            
                except Exception as e:
                    logging.error(f"Error in buffered reading: {e}")
                    time.sleep(0.01)
                    
        except Exception as e:
            logging.error(f"Failed to start buffered subprocess: {e}")
            self.running = False

    def _read_console_pexpect(self):
        """Method 2: Pexpect-based reading"""
        if not PEXPECT_AVAILABLE:
            logging.error("pexpect not available, falling back to buffered reading")
            self._read_console_buffered()
            return
            
        try:
            cmd = f"{self.c_program_path} {self.input_string or 'default_input'}"
            self.process = pexpect.spawn(cmd, encoding='utf-8', timeout=1)
            
            while self.running and not self.stop_event.is_set():
                try:
                    line = self.process.readline()
                    if line:
                        line = line.strip()
                        if line:
                            logging.debug(f"Pexpect read: {line}")
                            self.parse_and_queue(line)
                    elif not self.process.isalive():
                        break
                    else:
                        time.sleep(0.01)
                except pexpect.TIMEOUT:
                    continue
                except pexpect.EOF:
                    break
        except Exception as e:
            logging.error(f"Pexpect error: {e}")

    def _read_console_delayed(self):
        """Method 3: Delayed line processing"""
        try:
            cmd = [self.c_program_path]
            if self.input_string:
                cmd.append(self.input_string)
            else:
                cmd.append("default_input")
                
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            while self.running and not self.stop_event.is_set():
                line = self.process.stdout.readline().strip()
                if not line and self.process.poll() is not None:
                    break
                if line:
                    self._schedule_line_processing(line)
                    
        except Exception as e:
            logging.error(f"Delayed processing error: {e}")

    def _schedule_line_processing(self, line):
        """Schedule line for delayed processing"""
        self.line_counter += 1
        line_id = self.line_counter
        
        # Cancel previous timer for similar lines
        self._cancel_similar_line_timers(line)
        
        # Store the line
        self.pending_lines[line_id] = line
        
        # Create timer to process line after delay
        timer = threading.Timer(0.05, self._process_delayed_line, args=[line_id])
        self.line_timers[line_id] = timer
        timer.start()

    def _cancel_similar_line_timers(self, new_line):
        """Cancel timers for incomplete versions of the same line"""
        to_cancel = []
        for line_id, existing_line in self.pending_lines.items():
            if self._lines_are_related(existing_line, new_line):
                to_cancel.append(line_id)
        
        for line_id in to_cancel:
            if line_id in self.line_timers:
                self.line_timers[line_id].cancel()
                del self.line_timers[line_id]
                del self.pending_lines[line_id]

    def _lines_are_related(self, line1, line2):
        """Check if two lines are related"""
        return line1.startswith(line2) or line2.startswith(line1)

    def _process_delayed_line(self, line_id):
        """Process line after delay"""
        if line_id in self.pending_lines:
            line = self.pending_lines[line_id]
            logging.debug(f"Delayed processing: {line}")
            self.parse_and_queue(line)
            del self.pending_lines[line_id]
            if line_id in self.line_timers:
                del self.line_timers[line_id]

    def _start_async_reader(self):
        """Method 4: Start asyncio reader"""
        def run_async():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._read_console_async())
        
        threading.Thread(target=run_async, daemon=True).start()

    async def _read_console_async(self):
        """Async console reading"""
        try:
            cmd = [self.c_program_path]
            if self.input_string:
                cmd.append(self.input_string)
            else:
                cmd.append("default_input")
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            buffer = ""
            while self.running and not self.stop_event.is_set():
                try:
                    chunk = await asyncio.wait_for(
                        self.process.stdout.read(1024), 
                        timeout=0.1
                    )
                    
                    if not chunk:
                        if self.process.returncode is not None:
                            break
                        continue
                    
                    buffer += chunk.decode('utf-8')
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            logging.debug(f"Async read: {line}")
                            self.parse_and_queue(line)
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logging.error(f"Async read error: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"Async subprocess error: {e}")

    def _start_multiprocess_reader(self):
        """Method 5: Start multiprocessing reader"""
        self.mp_queue = MPQueue()
        
        # Start reader process
        self.reader_process = Process(
            target=self._read_in_separate_process,
            args=(self.mp_queue, self.c_program_path, self.input_string)
        )
        self.reader_process.start()
        
        # Start queue monitor thread
        self.queue_monitor_thread = threading.Thread(target=self._monitor_mp_queue)
        self.queue_monitor_thread.daemon = True
        self.queue_monitor_thread.start()

    @staticmethod
    def _read_in_separate_process(mp_queue, program_path, input_string):
        """Read console output in separate process"""
        try:
            cmd = [program_path]
            if input_string:
                cmd.append(input_string)
            else:
                cmd.append("default_input")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            buffer = ""
            while True:
                chunk = process.stdout.read(1)
                if not chunk:
                    if process.poll() is not None:
                        break
                    continue
                
                buffer += chunk
                
                if chunk == '\n':
                    line = buffer.strip()
                    if line:
                        mp_queue.put(line)
                        logging.debug(f"MP queued: {line}")
                    buffer = ""
                    
        except Exception as e:
            logging.error(f"Multiprocess reader error: {e}")

    def _monitor_mp_queue(self):
        """Monitor multiprocessing queue"""
        while self.running:
            try:
                if not self.mp_queue.empty():
                    line = self.mp_queue.get(timeout=0.1)
                    logging.debug(f"MP received: {line}")
                    self.parse_and_queue(line)
                else:
                    time.sleep(0.01)
            except:
                continue

    def _read_file_tail(self):
        """Method 6: File-based communication"""
        try:
            # Clear the temp file first
            with open(self.temp_output_file, 'w') as f:
                f.write("")
            
            # Start C program with file output
            cmd = [self.c_program_path]
            if self.input_string:
                cmd.append(self.input_string)
            else:
                cmd.append("default_input")
            cmd.extend(["--output-file", self.temp_output_file])
            
            self.process = subprocess.Popen(cmd)
            
            # Tail the file
            last_position = 0
            with open(self.temp_output_file, 'r') as f:
                f.seek(last_position)
                
                while self.running and not self.stop_event.is_set():
                    line = f.readline()
                    if line:
                        line = line.strip()
                        if line:
                            logging.debug(f"File tail read: {line}")
                            self.parse_and_queue(line)
                        last_position = f.tell()
                    else:
                        time.sleep(0.01)
                        
        except Exception as e:
            logging.error(f"File tail error: {e}")

    def parse_and_queue(self, line: str):
        """Original parse_and_queue method (unchanged)"""
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
                    if self.mode == "console":
                        expected_types.add('input_string')
                    if new_session % 2 == 0:
                        expected_types.add('key')
                    else:
                        expected_types.add('kbps_data')
                    missing_types = expected_types - self.session_data_types
                    if missing_types:
                        logging.warning(f"Session {self.current_session} missing data types: {missing_types}")
                        for data_type in missing_types:
                            if self.current_session == -1:
                                if data_type in ['timestamp_spd1', 'timestamp_spd2']:
                                    continue
                                elif data_type == 'key':
                                    self.data_queue.put({"type": "key", "value": "0" * 128, "length": 128})
                                    self.last_session_data["key"] = "0" * 128
                                    logging.info(f"Initialized missing {data_type} to '{'0' * 128}' for session {self.current_session}")
                                elif data_type == 'input_string' and self.mode == "console":
                                    self.data_queue.put({"type": "input_string", "value": "default_input"})
                                    self.last_session_data["input_string"] = "default_input"
                                    logging.info(f"Initialized missing {data_type} to 'default_input' for session {self.current_session}")
                                elif data_type != 'input_string':
                                    self.data_queue.put({"type": data_type, "value" if data_type != "kbps_data" else "kbps": 0})
                                    self.last_session_data[data_type] = 0
                                    logging.info(f"Initialized missing {data_type} to 0 for session {self.current_session}")
                            else:
                                if data_type in ['timestamp_spd1', 'timestamp_spd2']:
                                    for value in self.last_session_data[data_type]:
                                        self.data_queue.put({"type": data_type, "value": value})
                                elif self.last_session_data[data_type] is not None and data_type != 'input_string':
                                    if data_type == 'key':
                                        self.data_queue.put({"type": data_type, "value": self.last_session_data[data_type], "length": len(self.last_session_data[data_type])})
                                    elif data_type == 'kbps_data':
                                        self.data_queue.put({"type": data_type, "kbps": self.last_session_data[data_type]})
                                    else:
                                        self.data_queue.put({"type": data_type, "value": self.last_session_data[data_type]})
                                elif data_type == 'input_string' and self.mode == "console" and self.last_session_data['input_string'] is not None:
                                    self.data_queue.put({"type": "input_string", "value": self.last_session_data['input_string']})
                    self.current_session = new_session
                    self.spd1_values_mode = False
                    self.spd2_values_mode = False
                    self.spd1_count = 0
                    self.spd2_count = 0
                    self.session_data_types = set()
                    self.data_queue.put({"type": "session_number", "value": new_session})
                    self.last_session_data["timestamp_spd1"] = []
                    self.last_session_data["timestamp_spd2"] = []
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
                self.last_session_data["timestamp_spd1"].append(timestamp)
                self.spd1_count += 1
                self.session_data_types.add("timestamp_spd1")
                if self.spd1_count == 40:
                    logging.info(f"Completed queuing 40 SPD1 timestamps for session {self.current_session}")
                logging.debug(f"Current file position after SPD1: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if self.spd2_values_mode and self.spd2_count < 40:
                timestamp = int(line)
                self.data_queue.put({"type": "timestamp_spd2", "value": timestamp})
                self.last_session_data["timestamp_spd2"].append(timestamp)
                self.spd2_count += 1
                self.session_data_types.add("timestamp_spd2")
                if self.spd2_count == 40:
                    logging.info(f"Completed queuing 40 SPD2 timestamps for session {self.current_session}")
                logging.debug(f"Current file position after SPD2: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("DECOY_STATE_RANDOMNESS_AT_SPD1:"):
                value = float(line.split(':')[1])
                self.data_queue.put({"type": "spd1_decaystate", "value": value})
                self.last_session_data["spd1_decaystate"] = value
                self.session_data_types.add("spd1_decaystate")
                logging.debug(f"Current file position after spd1_decaystate: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("VISIBILITY_RATIO_IS:"):
                value = float(line.split(':')[1])
                self.data_queue.put({"type": "visibility", "value": value})
                self.last_session_data["visibility"] = value
                self.session_data_types.add("visibility")
                logging.debug(f"Current file position after visibility: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("SPD1_QBER_VALUE_IS:"):
                value = float(line.split(':')[1])
                self.data_queue.put({"type": "qber", "value": value})
                self.last_session_data["qber"] = value
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
                    self.last_session_data["key"] = key
                    self.session_data_types.add("key")
                    logging.debug(f"Queued key (length {len(key)}): {key[:40]}... for session {self.current_session}")
                    logging.debug(f"Current file position after key: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                else:
                    logging.error(f"Invalid key format: {line}")
                return

            if line.startswith("KEY_RATE_PER_SECOND_IS:"):
                kbps = float(line.split(':')[1])
                self.data_queue.put({"type": "kbps_data", "kbps": kbps})
                self.last_session_data["kbps_data"] = kbps
                self.session_data_types.add("kbps_data")
                logging.debug(f"Queued kbps: {kbps} for session {self.current_session}")
                logging.debug(f"Current file position after kbps: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

            if line.startswith("INPUT_STRING:") and self.mode == "console":
                input_str = line.split(':', 1)[1]
                self.data_queue.put({"type": "input_string", "value": input_str})
                self.last_session_data["input_string"] = input_str
                self.session_data_types.add("input_string")
                logging.debug(f"Queued input string: {input_str} for session {self.current_session}")
                logging.debug(f"Current file position after input_string: {self.file.tell() if self.mode == 'file' and self.file and not self.file.closed else 'N/A'}")
                return

        except Exception as e:
            logging.error(f"Error parsing line '{line}': {e}")

    def stop(self):
        if self.running:
            logging.info("Stopping data processor")
            self.running = False
            self.stop_event.set()
            
            # Stop console processes
            if self.mode == "console" and self.process:
                try:
                    self.process.kill()
                except:
                    pass
                self.process = None
            
            # Stop multiprocessing components
            if self.reader_process and self.reader_process.is_alive():
                self.reader_process.terminate()
                self.reader_process.join(timeout=1)
                if self.reader_process.is_alive():
                    self.reader_process.kill()
            
            # Stop file reading
            if self.mode == "file" and self.file and not self.file.closed:
                self.file_position = self.file.tell()
                logging.debug(f"Saved file position: {self.file_position}")
                self.file.close()
                self.file = None
            
            # Stop threads
            if self.thread:
                self.thread.join(timeout=0.1)
                self.thread = None
            
            if self.queue_monitor_thread:
                self.queue_monitor_thread.join(timeout=0.1)
                self.queue_monitor_thread = None
            
            # Cancel pending timers
            for timer in self.line_timers.values():
                timer.cancel()
            self.line_timers.clear()
            self.pending_lines.clear()

    def get_file_position(self):
        return self.file_position

    def close(self):
        self.stop()
        if self.mode == "console" and self.process:
            logging.info("Closing data processor")
            try:
                if self.process.stdout and not self.process.stdout.closed:
                    self.process.stdout.close()
                if self.process.stderr and not self.process.stderr.closed:
                    self.process.stderr.close()
            except:
                pass
            self.process = None

# Usage Examples:
"""
# Example 1: Using buffer method (default)
processor = DataProcessor(data_queue, mode="console", input_string="test", console_read_method="buffer")

# Example 2: Using pexpect (Unix/Linux only)
processor = DataProcessor(data_queue, mode="console", input_string="test", console_read_method="pexpect")

# Example 3: Using delayed processing
processor = DataProcessor(data_queue, mode="console", input_string="test", console_read_method="delayed")

# Example 4: Using async metho
