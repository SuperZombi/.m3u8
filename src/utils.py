import shutil
import subprocess
import os
import sys
import re

def get_ffmpeg_ver() -> dict:
    def find_ver(text) -> str:
        return text.splitlines()[0].split("ffmpeg version")[-1].strip().split()[0]
    def find_year(text) -> list:
        match = re.findall(r'\b([1-3][0-9]{3})\b', text)
        if match is not None:
            return match
    try:
        process = subprocess.Popen(["ffmpeg", "-version"], stdout=subprocess.PIPE, encoding=os.device_encoding(0))
        answer = process.communicate()[0]
        return {'ver': find_ver(answer.strip()), 'year': find_year(answer.strip())[-1]}
    except FileNotFoundError: return {}

def get_audio_duration(file) -> float:
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding=os.device_encoding(0))
    return float(result.stdout)

def durationToSeconds(hms) -> float:
    a = hms.split(":")
    seconds = (int(a[0])) * 60 * 60 + (int(a[1])) * 60 + (float(a[2]));
    return seconds

def get_full_filepath(filename):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    directory, file = os.path.split(filename)

    if not directory:
        directory = current_dir

    full_file_path = os.path.join(directory, file)
    return os.path.abspath(full_file_path)

def display_progress_bar(
    current: int, filesize: int, ch: str = "█", scale: float = 0.5
) -> None:
    columns = shutil.get_terminal_size().columns
    max_width = int(columns * scale)
    filled = int(round(max_width * current / float(filesize)))
    remaining = max_width - filled
    progress_bar = ch * filled + " " * remaining
    percent = round(100.0 * current / float(filesize), 1)
    text = f"[ ↳ ] |{progress_bar}| {percent}%\r"
    sys.stdout.write(text)
    sys.stdout.flush()

def clear_last_line(amount=1):
    os.system('')
    for i in range(amount):
        sys.stdout.write("\033[K") #clear line
        if i < amount-1:
            sys.stdout.write("\033[F") #back to previous line

def make_ffmpeg_command(command, duration, on_progress=None):
    process = subprocess.Popen(command, encoding=os.device_encoding(0), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    history = []
    with process.stdout as pipe:
        for line in pipe:
            line = line.strip()
            history.append(line)
            if "time=" in line:
                try:
                    result = re.search(r"\.*time=(.*?) ", line)
                    seconds = durationToSeconds(result.group(1))
                    if on_progress:
                        on_progress(seconds, duration, process)
                    else:
                        display_progress_bar(seconds, duration)
                except: None

    return process.wait(), history
