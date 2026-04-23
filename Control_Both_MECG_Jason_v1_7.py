# Jason Yang
# 04/23/2026
# Control two WhaleTeq MECG 2.0 devices simultaneously, running same case. Waits between each case.
# Capture images from two webcams at regular intervals while cases are running. Names output in ms(tSinceStart = int((time.time() - start) * 1000))
# Save images to per-device subfolders under a case-specific folder, and zips it.

from ctypes import *
from mecg20 import *
import os, platform
import time
import threading
from pathlib import Path
from ctypes import create_string_buffer
import cv2
import zipfile

# =============================== Camera ================================
class CamWorker:
    def __init__(self, device, name, interval_sec):
        self.device = device               # e.g. "/dev/v4l/by-id/usb-...-index0" or 0/1 on Windows
        self.name = name                   # "vista_cam" or "advance_cam"
        self.interval = interval_sec
        self.backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_V4L2
        self.thread = threading.Thread(target=self._run, name=f"cam-{name}", daemon=True)
        self.caseRunning = False

    def start(self): self.thread.start()

    def setCaseDir(self, case_dir):
        self.caseDir = case_dir

    def setCaseRunning(self, running):
        self.caseRunning = running
    
    def getCaseRunning(self):
        return self.caseRunning

    def _run(self):
        def open_cam():
            c = cv2.VideoCapture(self.device, self.backend)
            if not c.isOpened():
                c.release()
                return None
            # Warm up a couple frames
            for _ in range(2):
                c.read()
            return c
    
        cam = open_cam()
        print(f"[{self.name}] started ({self.device}) is_open={bool(cam)}")
        self.caseRunning = True

        if self.interval <= 0:
            # Ensure we have an open camera
            if cam is None:
                print(f"[{self.name}] failed to open camera on start; aborting video capture.")
                return
            frame_width  = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            (self.caseDir / self.name).mkdir(parents=True, exist_ok=True)
            out = cv2.VideoWriter(str(self.caseDir / self.name / "video.avi"), fourcc, fps=30, frameSize=(frame_width, frame_height))
            try:
                while self.getCaseRunning():
                    if shutdown.is_set():
                        print(f"[{self.name}] shutdown signal received; stopping capture.")
                        break
                    # Ensure we have an open camera
                    if cam is None:
                        cam = open_cam()
                        continue
                    ret, frame = cam.read()
                    if not ret:
                        print("Error: Failed to read frame from webcam.")
                        break
                    # Write the frame to the output file
                    out.write(frame)
            finally:
                if cam is not None:
                    cam.release()
                if out is not None:
                    out.release()
                print("[cam] Worker stopped; camera released.")
        else:
            next_deadline = time.monotonic()  # first capture ASAP once running
            # Backoff settings for reopen attempts
            backoff = 0.5  # seconds
            backoff_max = 8.0

            try:
                start = time.time()
                while self.getCaseRunning():
                    if shutdown.is_set():
                        print(f"[{self.name}] shutdown signal received; stopping capture.")
                        break
                    now = time.monotonic()
                    remaining = next_deadline - now
                    if remaining > 0:
                        time.sleep(remaining)
                        if not self.getCaseRunning():
                            next_deadline = time.monotonic()
                            continue

                    # Ensure we have an open camera
                    if cam is None:
                        cam = open_cam()
                        if cam is None:
                            print(f"[{self.name}] open failed; retrying in {backoff:.1f}s")
                            time.sleep(backoff)
                            backoff = min(backoff * 2, backoff_max)
                            continue
                        backoff = 0.5  # reset on success

                    # Try to grab a frame
                    ret, frame = cam.read()
                    if not ret:
                        print(f"[{self.name}] read() failed; reopening...")
                        cam.release()
                        cam = None
                        # light backoff before next attempt
                        time.sleep(0.25)
                        continue

                    # Save frame
                    if self.caseDir:
                        (self.caseDir / self.name).mkdir(parents=True, exist_ok=True)
                        tSinceStart = int((time.time() - start) * 1000)
                        fileName = f"{tSinceStart:09d}.png"
                        cv2.imwrite(str(self.caseDir / self.name / fileName), frame)

                    next_deadline = time.monotonic() + self.interval
            finally:
                if cam is not None:
                    cam.release()
                print("[cam] Worker stopped; camera released.")

# Device Class
class Device:
    def __init__(self, name, dll_path, cam_path, pause_duration = 1, interval_sec = 1, suffix=None, zipResults=False):
        self.name = name                   # "advance" or "vista"
        self.dll_path = dll_path
        self.cam_path = cam_path
        self.suffix = suffix
        self.thread = threading.Thread(target=self._run, name=f"device-{name}", daemon=True)
        self.connected = threading.Event()
        self.connectedCb = ConnectedCallback(self.DeviceConnectedHandler)
        self.delayCb = OutputDelayCallback(self.OutputDelayHandler)
        self.outputCb = OutputSignalExCallback(self.OutputSignalHandler)
        self.case_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self.interval_sec = interval_sec
        self.firstCaseFlag = True
        self.caseRunning = False
        self.zipResults= zipResults
        self.pauseDuration = 60 * pause_duration

    def start(self, case_index):
        self.case_index = case_index
        self.thread.start()

    def initialize_device(self, second=False):
        # Join previous cam thread if it exists
        if hasattr(self, 'cam') and self.cam.thread.is_alive():
            self.cam.thread.join(timeout=10.0)
            if self.cam.thread.is_alive():
                print(f"[{self.name}] Warning: previous cam thread did not finish in time")
        
        self.cam = CamWorker(self.cam_path, f"{self.name}_cam", interval_sec=self.interval_sec)
        self.device = MECG20(self.dll_path)
        self.device.init(self.connectedCb)
        if second:
            self.connected.wait(timeout=5.0)
            if not self.connected.is_set():
                print("Error: device did not report connected in time.")
                return
        self.device.enable_loop(False)

    def DeviceConnectedHandler(self, connected):
        print('{} is {}connected{}'.format(
            self.name,
            '' if connected else 'dis',
            f" ({self.device.get_serial_number()})" if connected else '')
        )
        self.connected.set()

    # On case end, mark done and try to start next case
    def OutputSignalHandler(self, total_time, cb_time, voltage_struct, end):
        if end:
            print(f"[{self.name}] case {self.case_index} ended at t={total_time:.3f}s")
            with self.case_lock:
                self.case_index += 1
            self.cleanup()

    def OutputDelayHandler(self, delay_time):
        # self.cam.addDelay(delay_time)
        print(f"[{self.name}] output delay:", delay_time)

    def set_header(self, WHALETEQ_FILE):
        self.header = self.device.load_whaleteq_database(create_string_buffer(WHALETEQ_FILE.encode("ascii")))
    
    def get_running_state(self):
        with self._state_lock:
            return self.caseRunning

    def set_case_folder(self, case_index):
        # Try to start next case
        WHALETEQ_FILE = str(files[case_index])
        case_path = Path(WHALETEQ_FILE)
        # case_path = case_path.parent / case_path.stem
        case_path = OUTPUT_ROOT / case_path.stem
        case_path.mkdir(parents=True, exist_ok=True)
        self.cam.setCaseDir(case_path)
        print(f"{self.name} case folder set: {case_path}")
        self.set_header(WHALETEQ_FILE)
        return case_path
    

    def cleanup(self):
        print(f"\n{self.name} - Stopping output and cleaning up...")
        for label, fn in [
            ("cam stop",    lambda: self.cam.setCaseRunning(False)),
            ("stop_output", lambda: self.device.stop_output()),
            ("free_header", lambda: self.device.free_ecg_header(self.header) if self.header else None),
            ("device free", lambda: self.device.free()),
        ]:
            try:
                fn()
            except Exception as e:
                print(f"[{self.name}] cleanup warning ({label}): {e}")

        # Wait for cam thread to finish
        if hasattr(self, 'cam'):
            self.cam.thread.join(timeout=15.0)
            if self.cam.thread.is_alive():
                print(f"[{self.name}] Warning: cam thread did not finish in time; skipping zip.")
            elif self.zipResults:
                case_dir = getattr(self.cam, 'caseDir', None)
                if case_dir:
                    local_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
                    suffix_part = f"_{self.suffix}" if self.suffix else ""
                    zip_directory(str(case_dir), f'{case_dir}_{local_time}{suffix_part}.zip')

        self.connected.clear()
        with self._state_lock:
            self.caseRunning = False

    def _run(self):
        while not shutdown.is_set():
            time.sleep(0.1)
            if not self.get_running_state():
                if not self.firstCaseFlag:
                    local_time = time.ctime(time.time())
                    print(f"{local_time}: Waiting {self.pauseDuration/60:.1f} min to start next case.")
                    shutdown.wait(timeout=self.pauseDuration)
                    if shutdown.is_set():
                        break
                self.firstCaseFlag = False
                local_time = time.ctime(time.time())
                print(f"{local_time}, [{self.name}] attempting case {self.case_index}")
                self.start_next_case()

    def start_next_case(self):
        with self._state_lock:
            self.caseRunning = True
        with self.case_lock:
            current_index = self.case_index
        self.initialize_device(second=True)
        self.case_path = self.set_case_folder(current_index)
        self.cam.start()
        started = self.device.output_waveform(0, self.outputCb, self.delayCb)
        if started:
            local_time = time.ctime(time.time())
            print(f"{local_time}, [{self.name}] started case {self.case_index} - saving images to {self.case_path}/{self.cam.name}")
        else:
            local_time = time.ctime(time.time())
            print(f"{local_time}, [{self.name}] failed to start case {self.case_index}. No more cases.")
            shutdown.set()



def zip_directory(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, dir_files in os.walk(folder_path):
            for file in dir_files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))

# =============================== WhaleTeq control ================================


folder = Path(r"C:\Users\PASCALL EMPLOYEE\OneDrive\OneDrive - PASCALL SYSTEMS\Trong Nguyen's files - EEG")
OUTPUT_ROOT = Path(r"D:\Sed_BIS_Record") # save to ssd
files = sorted(folder.glob("*.txt"))  # list of whaleteq case files, sorted alphabetically
cam1_path = 2
cam2_path = 1
shutdown = threading.Event()
case_index = 0


def main():
    global device1, device2, case_index
    
    # MECG Connection
    device1 = Device("Advance", "mecgFiles\\MECG20x64.dll", cam1_path,
                     interval_sec=0,  # Interval_sec is the seconds between each frame (float)
                     pause_duration=5, # Pause between cases to settle (minutes)
                     suffix="", # Suffix added to end of zip folder names for labelling
                     zipResults=False, # zip up case results at end of case
                     )
    device2 = Device("Root1", "mecgFiles\\MECG20x64.2.dll", cam2_path,
                     interval_sec=0,  # Set interval_sec=0 to save as video instead of individual frames
                     pause_duration=5,
                     suffix="",
                     zipResults=False,
                     )

    # Start case 0 on both
    print("\n--- Starting cases on both devices ---")
    device1.start(case_index)
    device2.start(case_index)

    # Run until all cases are done
    print("\nRunning cases... (will auto-advance when both devices finish each case)")
    try:
        while not shutdown.is_set():
            time.sleep(0.1)  # light wait; callbacks drive progression
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        device1.cleanup()
        device2.cleanup()
        local_time = time.ctime(time.time())
        print(f"{local_time}, done")

if __name__ == "__main__":
    main()
