import customtkinter
from tkinter import messagebox
from CTkMessagebox import CTkMessagebox
import os, sys
from utils import *
from functools import partial
from frames import *
from argparse import ArgumentParser

__version__ = '2.0.0'

# customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
# customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green


class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		self.title("M3U8 Video Downloader")
		self.geometry("400x400")
		self.minsize(300, 350)
		self.protocol("WM_DELETE_WINDOW", self.on_closing)

		self.appConfig = {}
		self.appConfig['accentColor'] = customtkinter.ThemeManager.theme['CTkButton']['fg_color'][0]

		if getattr(sys, 'frozen', False):
			self.appConfig['app_path'] = sys.executable
			self.appConfig['run_as'] = "exe"
		else:
			self.appConfig['app_path'] = os.path.realpath(__file__)
			self.appConfig['run_as'] = "python"
			self.appConfig['python_path'] = sys.executable

		# Header menu
		container = customtkinter.CTkFrame(self, corner_radius=0)
		container.pack(fill="x")
		self.menuFrames = {}

		def generate_frames(navigation_buttons):
			for index, (tab_name, tab) in enumerate(navigation_buttons.items()):
				customtkinter.CTkFrame(self, fg_color="transparent")
				container.grid_columnconfigure(index, weight=1)
				button = customtkinter.CTkButton(container, text=tab['text'], command=partial(self.change_tab, tab_name),
										corner_radius=0, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
				button.grid(row=0, column=index, sticky="ew")
				self.menuFrames[tab_name] = {"button": button, "frame": tab['frame'](self)}
				

		generate_frames({
			"home": {"text": "Home", "frame": HomeFrame},
			"settings": {"text": "Settings", "frame": SettingsFrame}
		})
		
		customtkinter.CTkLabel(self, text="M3U8 VIDEO DOWNLOADER", font=("", 16, 'bold'), text_color=self.appConfig['accentColor']).pack(pady=8)


	def on_closing(self):
		for frame in self.menuFrames.values():
			frame["frame"].on_closing()
		self.destroy()

	def onload(self):
		self.parse_args()
		self.change_tab("home")

		info = get_ffmpeg_ver()
		if not info.get('ver'):
			self.showError("FFmpeg is not installed!")
			return self.destroy()

		for frame in self.menuFrames.values():
			frame["frame"].onload()

		self.mainloop()

	def parse_args(self):
		parser = ArgumentParser()
		parser.add_argument('-browser', '--browser')
		self.args = parser.parse_args()

	def change_tab(self, target):
		for frame in self.menuFrames.values():
			frame["frame"].pack_forget()
			frame["button"].configure(fg_color="transparent")

		self.menuFrames[target]["frame"].pack(fill='both', expand=1)
		self.menuFrames[target]["button"].configure(fg_color=("gray75", "gray25"))

	def showError(self, text):
		msg = CTkMessagebox(title="Error", message=text, icon="warning", option_1="Cancel")
		return msg.get()

	def fileAreadyExists(self, filename) -> bool:
		msg = CTkMessagebox(title="File already exists", message=f"Overwrite file {filename}?",
							icon="question", option_1="No", option_2="Yes")
		msg.info._text_label.configure(wraplength=msg.width)
		return msg.get() == "Yes"

	def open_file(self, file):
		if os.path.exists(file):
			os.system(f'explorer /select,"{file}"')


app = App()
app.onload()
