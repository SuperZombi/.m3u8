from utils import *
import customtkinter

class SettingsFrame(MyTabFrame):
	def __init__(self, master):
		super().__init__(master)

		container = customtkinter.CTkFrame(self, fg_color='transparent')
		container.pack(padx=20, pady=8, fill="x")
		container.grid_columnconfigure((0, 1), weight=1)

		customtkinter.CTkButton(container, text="Install application", command=self.installApp
		).grid(column=0, row=0)
		customtkinter.CTkButton(container, text="Uninstall application", command=self.installApp
		).grid(column=1, row=0)


	def onload(self):
		pass

	def installApp(self):
		print("here")