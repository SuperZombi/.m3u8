import customtkinter

# customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
# customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

accentColor = customtkinter.ThemeManager.theme['CTkButton']['fg_color'][0]

class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		self.title("M3U8 Video Downloader")
		self.geometry("400x400")

		customtkinter.CTkLabel(self, text="M3U8 VIDEO DOWNLOADER", font=("", 16, 'bold'), text_color=accentColor).pack(pady=8)

		customtkinter.CTkLabel(self, text="Video URL (.m3u8):", font=("", 14)).pack()
		self.videoUrl = customtkinter.CTkEntry(self, placeholder_text="URL of the video (.m3u8)", justify="center", font=("", 12))
		self.videoUrl.pack(padx=20, pady=(0, 8), fill="x")
		self.videoUrl.bind("<KeyRelease>", self.onInput)

		customtkinter.CTkLabel(self, text="Target folder:", font=("", 14)).pack()
		container = customtkinter.CTkFrame(master=self, fg_color='transparent')
		container.pack(padx=20, pady=(0, 8), fill="x")
		container.grid_columnconfigure(0, weight=50)
		container.grid_columnconfigure(1, weight=1)

		self.targetFolder = customtkinter.CTkEntry(container, placeholder_text="Target folder", justify="center", state="disabled", font=("", 12))
		self.targetFolder.grid(column=0, row=0, sticky='we')
		customtkinter.CTkButton(container, text="📁", width=10, command=self.openTargetFolderDialog
		).grid(column=1, row=0, sticky='e')

		customtkinter.CTkLabel(self, text="File name (with extension):", font=("", 14)).pack()
		self.fileName = customtkinter.CTkEntry(self, placeholder_text="File_name.mp4", justify="center", font=("", 12))
		self.fileName.pack(padx=20, pady=(0, 8), fill="x")
		self.fileName.bind("<KeyRelease>", self.onInput)

		self.startButton = customtkinter.CTkButton(self, text="Download", command=self.button_callbck, state="disabled")
		self.startButton.pack(side="bottom", pady=8)

	def button_callbck(self):
		print("button clicked")

	def openTargetFolderDialog(self):
		folder = customtkinter.filedialog.askdirectory()
		if folder:
			self.targetFolder.configure(state='normal')
			self.targetFolder.insert(0, folder)
			self.targetFolder.configure(state='disabled')
			self.onInput("")

	def checkWidgetsFilled(self):
		widgets = [self.videoUrl, self.targetFolder, self.fileName]
		for widget in widgets:
			if widget.get().strip() == "":
				return False
		return True

	def onInput(self, event):
		if self.checkWidgetsFilled():
			self.startButton.configure(state='normal')
		else:
			self.startButton.configure(state='disabled')


app = App()
app.mainloop()
