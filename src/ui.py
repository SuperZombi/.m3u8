import customtkinter
from tkinter import messagebox
from CTkMessagebox import CTkMessagebox
import os
from utils import *
import threading

__version__ = '3.0.0'

# customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
# customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

accentColor = customtkinter.ThemeManager.theme['CTkButton']['fg_color'][0]

class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		self.title("M3U8 Video Downloader")
		self.geometry("400x400")
		self.protocol("WM_DELETE_WINDOW", self.on_closing)

		customtkinter.CTkLabel(self, text="M3U8 VIDEO DOWNLOADER", font=("", 16, 'bold'), text_color=accentColor).pack(pady=8)

		customtkinter.CTkLabel(self, text="Video URL (.m3u8):", font=("", 14)).pack()
		self.videoUrl = customtkinter.CTkEntry(self, placeholder_text="URL of the video (.m3u8)", justify="center", font=("", 12))
		self.videoUrl.pack(padx=20, pady=(0, 8), fill="x")
		self.videoUrl.bind("<KeyRelease>", self.onInput)

		customtkinter.CTkLabel(self, text="Target folder:", font=("", 14)).pack()
		container = customtkinter.CTkFrame(master=self, fg_color='transparent')
		container.pack(padx=20, pady=(0, 8), fill="x")
		container.grid_columnconfigure(0, weight=100)
		container.grid_columnconfigure(1, weight=1)

		self.targetFolder = customtkinter.CTkEntry(container, placeholder_text="Target folder", justify="center", state="disabled", font=("", 12))
		self.targetFolder.grid(column=0, row=0, sticky='we')
		customtkinter.CTkButton(container, text="📁", width=10, command=self.openTargetFolderDialog
		).grid(column=1, row=0, sticky='e')

		customtkinter.CTkLabel(self, text="File name and extension:", font=("", 14)).pack()
		container = customtkinter.CTkFrame(master=self, fg_color='transparent')
		container.pack(padx=20, pady=(0, 8), fill="x")
		container.grid_columnconfigure(0, weight=100)
		container.grid_columnconfigure(1, weight=1)

		self.fileName = customtkinter.CTkEntry(container, placeholder_text="File_name", justify="center", font=("", 12))
		self.fileName.grid(column=0, row=0, sticky='we')
		self.fileName.bind("<KeyRelease>", self.onInput)

		self.fileExt = customtkinter.CTkEntry(container, placeholder_text="mp4", justify="center", width=50, font=("", 12))
		self.fileExt.grid(column=1, row=0, sticky='e')
		self.fileExt.bind("<KeyRelease>", self.onInput)

		self.progressWrapper = customtkinter.CTkFrame(master=self, fg_color='transparent')
		self.progressWrapper.grid_columnconfigure(0, weight=20)
		self.progressWrapper.grid_columnconfigure(1, weight=1)

		self.progressbar = customtkinter.CTkProgressBar(self.progressWrapper, orientation="horizontal")
		self.progressbar.grid(column=0, row=0, sticky='we')
		self.progressValue = customtkinter.CTkLabel(self.progressWrapper, text="100%", font=("", 14))
		self.progressValue.grid(column=1, row=0)

		self.startButton = customtkinter.CTkButton(self, text="Download", command=self.start_work, state="disabled")
		self.startButton.pack(side="bottom", pady=8)

	def on_closing(self):
		self.stopProcess=True
		self.destroy()

	def onload(self):
		self.fileExt.insert(0, "mp4")
		self.onInput("")

		info = get_ffmpeg_ver()
		if not info.get('ver'):
			self.showError("FFmpeg is not installed!")
			return self.destroy()
		self.setTargetFolder(os.getcwd())
		self.mainloop()

	def setTargetFolder(self, value):
		self.targetFolder.configure(state='normal')
		self.targetFolder.delete(0, "end")
		self.targetFolder.insert(0, value)
		self.targetFolder.configure(state='disabled')
		self.onInput("")

	def openTargetFolderDialog(self):
		folder = customtkinter.filedialog.askdirectory()
		if folder:
			self.setTargetFolder(folder)

	def checkWidgetsFilled(self):
		widgets = [self.videoUrl, self.targetFolder, self.fileName, self.fileExt]
		for widget in widgets:
			if widget.get().strip() == "":
				return False
		return True

	def onInput(self, event):
		if self.checkWidgetsFilled():
			self.startButton.configure(state='normal')
		else:
			self.startButton.configure(state='disabled')

	def showError(self, text):
		msg = CTkMessagebox(title="Error", message=text, icon="warning", option_1="Cancel")
		return msg.get()

	def fileAreadyExists(self, filename) -> bool:
		msg = CTkMessagebox(title="File already exists", message=f"Remove file {filename}?",
							icon="question", option_1="No", option_2="Yes")
		return msg.get() == "Yes"

	def resetStartButton(self):
		self.startButton.configure(text="Download")
		self.startButton.configure(command=self.start_work)
		self.progressWrapper.pack_forget()
		self.update()

	def start_work(self):
		self.targetFile = os.path.join(self.targetFolder.get(), self.fileName.get() + "." + self.fileExt.get())
		self.m3u8 = self.videoUrl.get()
		if os.path.exists(self.targetFile):
			result = self.fileAreadyExists(self.targetFile)
			if not result: return
			os.remove(self.targetFile)

		self.progressbar.set(0)
		self.progressValue.configure(text="0%")
		self.progressWrapper.pack(side="bottom", pady=8, padx=20, fill="x")

		self.stopProcess = False
		def stopFunc():
			self.stopProcess=True
		self.startButton.configure(text="Stop")
		self.startButton.configure(command=stopFunc)
		self.update()

		threading.Thread(target=self.work_wrapper).start()

	def work_wrapper(self):
		duration = get_audio_duration(self.m3u8)

		if self.stopProcess:
			self.resetStartButton()
		def progress(current, total, process):
			if self.stopProcess:
				process.kill()
				self.resetStartButton()
			percent = round(current / total, 2)
			self.progressbar.set(percent)
			self.progressValue.configure(text=str(round(percent*100))+"%")
			self.update()

		make_ffmpeg_command(["ffmpeg", "-reconnect", "1",
                        "-reconnect_at_eof", "1",
                        "-reconnect_streamed", "1",
                        "-reconnect_delay_max", "2",
                        "-protocol_whitelist", "file,http,https,tcp,tls",
                        "-i", self.m3u8,
                        self.targetFile], duration=duration, on_progress=progress)
		self.on_finish()

	def on_finish(self):
		self.startButton.configure(text="Open")
		self.startButton.configure(command=self.open_file)

	def open_file(self):
		if os.path.exists(self.targetFile):
			os.system(f'explorer /select,"{self.targetFile}"')
			self.after(3000, self.resetStartButton)


app = App()
app.onload()
