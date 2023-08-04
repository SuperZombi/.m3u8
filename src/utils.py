import subprocess
import os, sys
import re
from customtkinter import CTkFrame

startupinfo = None
if os.name == 'nt':
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


class MyTabFrame(CTkFrame):
	def __init__(self, master):
		super().__init__(master, fg_color="transparent")
		self.master = master

	def onload(self): pass
	def on_closing(self): pass


def resource_path(relative_path):
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

def ffmpeg() -> str:
	f = os.path.join(resource_path("ffmpeg"), "ffmpeg.exe")
	return f if os.path.exists(f) else "ffmpeg"
def ffprobe() -> str:
	f = os.path.join(resource_path("ffmpeg"), "ffprobe.exe")
	return f if os.path.exists(f) else "ffprobe"

def get_ffmpeg_ver() -> dict:
	def find_ver(text) -> str:
		return text.splitlines()[0].split("ffmpeg version")[-1].strip().split()[0]
	def find_year(text) -> list:
		match = re.findall(r'\b([1-3][0-9]{3})\b', text)
		if match is not None:
			return match
	try:
		process = subprocess.Popen([ffmpeg(), "-version"], stdout=subprocess.PIPE, startupinfo=startupinfo)
		answer = process.communicate()[0]
		try:
			answer = answer.decode('utf-8')
		except UnicodeDecodeError:
			answer = answer.decode(os.device_encoding(0))
		return {'ver': find_ver(answer.strip()), 'year': find_year(answer.strip())[-1]}
	except FileNotFoundError: return {}

def get_audio_duration(file) -> float:
	result = subprocess.run([ffprobe(), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file],
							stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding=os.device_encoding(0), startupinfo=startupinfo)
	return float(result.stdout)

def durationToSeconds(hms) -> float:
	a = hms.split(":")
	seconds = (int(a[0])) * 60 * 60 + (int(a[1])) * 60 + (float(a[2]));
	return seconds

def openExplorer(path):
	CREATE_NO_WINDOW = 0x08000000
	if not os.path.exists(path): return
	if os.path.isdir(path):
		subprocess.run(["explorer", path], creationflags=CREATE_NO_WINDOW)
	elif os.path.isfile(path):
		subprocess.run(["explorer", '/select,', path], creationflags=CREATE_NO_WINDOW)


def make_ffmpeg_command(command, duration, on_progress=None):
	process = subprocess.Popen(command, encoding=os.device_encoding(0), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=startupinfo)
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
				except: None

	return process.wait(), history
