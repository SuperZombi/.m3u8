from utils import *
import customtkinter
import threading
import urllib.parse as urlparse

class HomeFrame(MyTabFrame):
	def __init__(self, master):
		super().__init__(master)

		customtkinter.CTkLabel(self, text="Video URL:", font=("", 14)).pack()
		self.videoUrl = customtkinter.CTkEntry(self, placeholder_text="URL of the video (.m3u8)", justify="center", font=("", 12))
		self.videoUrl.pack(padx=20, pady=(0, 8), fill="x")
		self.videoUrl.bind("<KeyRelease>", self.onInput)

		customtkinter.CTkLabel(self, text="Output folder:", font=("", 14)).pack()
		container = customtkinter.CTkFrame(self, fg_color='transparent')
		container.pack(padx=20, pady=(0, 8), fill="x")
		container.grid_columnconfigure(0, weight=100)
		container.grid_columnconfigure(1, weight=1)

		self.targetFolder = customtkinter.CTkEntry(container, placeholder_text="Target folder", justify="center", state="disabled", font=("", 12))
		self.targetFolder.grid(column=0, row=0, sticky='we')
		customtkinter.CTkButton(container, text="📁", width=10, command=self.openTargetFolderDialog
		).grid(column=1, row=0, sticky='e')

		customtkinter.CTkLabel(self, text="File name and extension:", font=("", 14)).pack()
		container = customtkinter.CTkFrame(self, fg_color='transparent')
		container.pack(padx=20, pady=(0, 8), fill="x")
		container.grid_columnconfigure(0, weight=100)
		container.grid_columnconfigure(1, weight=1)

		self.fileName = customtkinter.CTkEntry(container, placeholder_text="File_name", justify="center", font=("", 12))
		self.fileName.grid(column=0, row=0, sticky='we')
		self.fileName.bind("<KeyRelease>", self.onInput)

		self.fileExt = customtkinter.CTkEntry(container, placeholder_text="mp4", justify="center", width=50, font=("", 12))
		self.fileExt.grid(column=1, row=0, sticky='e')
		self.fileExt.bind("<KeyRelease>", self.onInput)

		self.progressWrapper = customtkinter.CTkFrame(self, fg_color='transparent')
		self.progressWrapper.grid_columnconfigure(0, weight=20)
		self.progressWrapper.grid_columnconfigure(1, weight=1)

		self.progressbar = customtkinter.CTkProgressBar(self.progressWrapper, orientation="horizontal")
		self.progressbar.grid(column=0, row=0, sticky='we')
		self.progressValue = customtkinter.CTkLabel(self.progressWrapper, text="100%", font=("", 14))
		self.progressValue.grid(column=1, row=0)

		self.startButton = customtkinter.CTkButton(self, text="Download", command=self.start_work, state="disabled")
		self.startButton.pack(side="bottom", pady=8)

		self.master.bind('<Return>', self.start_work)

	def onload(self):
		self.allowedProtocols = ("http://", "https://")
		self.fileExt.insert(0, "mp4")
		self.onInput("")

		self.setTargetFolder(os.path.dirname(self.master.appConfig['app_path']))
		self.parse_args()

	def on_closing(self):
		self.stopProcess=True

	def parse_args(self):
		if self.master.args.browser:
			url = self.master.args.browser
			params = dict(urlparse.parse_qsl(urlparse.urlparse(url).query))
			self.videoUrl.insert(0, params['url'])
			self.fileName.insert(0, params['name'])
			self.onInput("")

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
		if not self.videoUrl.get().startswith(self.allowedProtocols):
			return False
		return True

	def onInput(self, event):
		if self.checkWidgetsFilled():
			self.startButton.configure(state='normal')
		else:
			self.startButton.configure(state='disabled')

	def resetStartButton(self):
		self.startButton.configure(text="Download")
		self.startButton.configure(command=self.start_work)
		self.progressWrapper.pack_forget()
		self.master.update()

	def start_work(self, event=None):
		if not self.checkWidgetsFilled(): return

		self.targetFile = os.path.join(self.targetFolder.get(), self.fileName.get() + "." + self.fileExt.get())
		self.m3u8 = self.videoUrl.get()
		if os.path.exists(self.targetFile):
			result = self.master.fileAreadyExists(self.targetFile)
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
		self.master.update()

		threading.Thread(target=self.work_wrapper).start()

	def work_wrapper(self):
		try:
			duration = get_audio_duration(self.m3u8)
		except:
			self.master.showError("Can't download this video")
			self.stopProcess = True

		if self.stopProcess:
			return self.resetStartButton()
			
		def progress(current, total, process):
			if self.stopProcess:
				process.kill()
				self.resetStartButton()
			percent = round(current / total, 2)
			self.progressbar.set(percent)
			self.progressValue.configure(text=str(round(percent*100))+"%")
			self.master.update()

		result = make_ffmpeg_command(["ffmpeg", "-reconnect", "1",
									"-reconnect_at_eof", "1",
									"-reconnect_streamed", "1",
									"-reconnect_delay_max", "2",
									"-protocol_whitelist", "file,http,https,tcp,tls",
									"-i", self.m3u8, self.targetFile],
									duration=duration, on_progress=progress)
		if result[0] == 0:
			self.on_finish()

	def on_finish(self):
		self.startButton.configure(text="Open")
		self.startButton.configure(command=self.open_file)

	def open_file(self):
		self.master.open_file(self.targetFile)
		self.after(3000, self.resetStartButton)
