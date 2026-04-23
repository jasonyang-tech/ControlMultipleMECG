# 04/20/2026
# convert_to_whaleteq_format.py
# Converts a generated signal .csv/.edf/.bdf into a whaleteq MECG .txt format.

# %%
import pathlib
import numpy as np
import mne
import pandas as pd
import os

def add_wave_to_text(lines, wave, header):
    wave = wave.astype(np.int16)
    lines.append(header)
    lines.extend(str(sample) for sample in wave)
    return lines

# %%
# See MECG documentation. CHANGE in the future to better represent the behavior the MECG output.
# the MECG alters output data on the V1-6 leads based on the value of the Wilson terminal
def convECGtoEEG(vList, lead1, lead2):
    scaledList = pd.DataFrame([val1 - ((val2 + val3) / 3) for val1, val2, val3 in zip(vList, lead1, lead2)])
    # print(f"Wilson - {scaledList}")
    print(scaledList.describe())
    return np.array(scaledList.squeeze())

def extract_channel_data(raw, wanted):
    eeg_channels = [ch for ch in raw.ch_names if any(w in ch for w in wanted)]
    if not eeg_channels:
        raise ValueError("EEG channels not found")
    data = raw.get_data(units='uV', picks=eeg_channels)
    return data, eeg_channels


def convert_to_whaleteq_format(file_path, sample_rate = 250):
    # get data and channel names based on file type
    file_extension = file_path.lower()[-4::]
    match file_extension:
        case ".edf":
            output_file_path = file_path.replace(".edf", ".txt")
            print(output_file_path)
            if os.path.exists(output_file_path):
                print("File already exists")
                return
            raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
            wanted = {"FP1", "FP2", "F7", "F8"}
            data, eeg_channels = extract_channel_data(raw, wanted)
        case ".bdf":
            output_file_path = file_path.replace(".bdf", ".txt")
            print(output_file_path)
            if os.path.exists(output_file_path):
                print("File already exists")
                return
            raw = mne.io.read_raw_bdf(file_path, preload=True, verbose=False)
            wanted = {"L1", "L2", "R1", "R2"}
            data, eeg_channels = extract_channel_data(raw, wanted)
        case ".csv":
            output_file_path = file_path.replace(".csv", ".txt")
            print(output_file_path)
            if os.path.exists(output_file_path):
                print("File already exists")
                return
            df = pd.read_csv(file_path)
            eeg_channels = df.columns.tolist()
            data = []
            for i in range(len(df.columns)):
                data.append(df.iloc[:, i].values)
    

    for column in eeg_channels:
        print(f"Column: {column}")
    data = list(data[:8])
    zeros_channel = np.zeros(len(data[0]))
    for i in range(8-len(data)):
        data.append(zeros_channel)

    # Write to whaleteq format. Map each read channel to Vn
    lines = [str(sample_rate), str(len(data[0])), "start"]
    lines = add_wave_to_text(lines, data[6], "Lead I")
    lines = add_wave_to_text(lines, data[7], "Lead II")
    lines = add_wave_to_text(lines, convECGtoEEG(data[0], data[6], data[7]), "V1")
    lines = add_wave_to_text(lines, convECGtoEEG(data[1], data[6], data[7]), "V2")
    lines = add_wave_to_text(lines, convECGtoEEG(data[2], data[6], data[7]), "V3")
    lines = add_wave_to_text(lines, convECGtoEEG(data[3], data[6], data[7]), "V4")
    lines = add_wave_to_text(lines, convECGtoEEG(data[4], data[6], data[7]), "V5")
    lines = add_wave_to_text(lines, convECGtoEEG(data[5], data[6], data[7]), "V6")

    with open(output_file_path, "w") as text_file:
        text_file.write("\n".join(lines) + "\n")



def batch_convert_edf_to_whale_teq(input_dir, sample_rate = 250, case_list = None):
    """
    Converts all .edf files in input_dir to WhaleTeq .txt format.
    
    Args:
        input_dir:  folder containing your .edf files
        sample_rate:  sample rate of input files, for output files
        case_list:  optional .csv file with case names in the first column to filter
    """

    supported = {".edf", ".bdf", ".csv"}
    files = [
        f for f in pathlib.Path(input_dir).iterdir()
        if f.suffix.lower() in supported
    ]
    if case_list is not None:
        # --- Load case names from the first column ---
        cases_df = pd.read_csv(case_list, header=0, usecols=[0])
        target_stems = {
            pathlib.Path(str(name).strip()).stem
            for name in cases_df.iloc[:, 0]
            if pd.notna(name)
        }

        if not target_stems:
            print("Case list is empty — nothing to convert.")
            return
        matched = [f for f in files if any(f.stem.startswith(stem) for stem in target_stems)]
        files = matched

    print(f"Found {len(files)} file(s). Starting conversion...\n")
    succeeded, failed = [], []

    for i, fname in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Converting: {fname.name}")
        try:
            convert_to_whaleteq_format(str(fname), sample_rate=sample_rate)
            succeeded.append(fname)
        except Exception as e:
            print(f"Failed: {e}")
            failed.append((fname, str(e)))

    print(f"\nDone. {len(succeeded)} succeeded, {len(failed)} failed.")
    if failed:
        print("\nFailed files:")
        for fname, err in failed:
            print(f"  {fname}: {err}")


filepath = "Usability_test_case_2025_10.csv" # CHANGE based on file name
# convert_to_whaleteq_format(filepath, 500)

batch_convert_edf_to_whale_teq(
    input_dir=r"C:\Users\Electronics Engineer\OneDrive - PASCALL SYSTEMS (1)\Trong Nguyen's files - EEG", # CHANGE to .edf folder
    sample_rate=250,
    case_list=r"C:\Users\Electronics Engineer\Downloads\MGH BS.csv"
)
print("File conversion done.")

