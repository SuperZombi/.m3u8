from utils import *
import customtkinter
import os

class SettingsFrame(MyTabFrame):
	def __init__(self, master):
		super().__init__(master)
		self.protocol = "m3u8"

		customtkinter.CTkLabel(self, text=f"version: {self.master.__version__}", font=("", 15)).pack(pady=(0, 8))

		container = customtkinter.CTkFrame(self)
		container.pack(padx=20, pady=8, fill="x")
		container.grid_columnconfigure((0, 1), weight=1)

		customtkinter.CTkButton(container, text="Install application", command=self.installApp
		).grid(column=0, row=0, pady=10)
		customtkinter.CTkButton(container, fg_color="red", hover_color="darkred", text="Uninstall application", command=self.uninstallApp
		).grid(column=1, row=0, pady=10)


	def onload(self):
		pass

	def on_closing(self):
		if self.master.appConfig['run_as'] == "python":
			files = [resource_path("register_protocol.reg"), resource_path("uninstall.reg")]
			for file in files:
				if os.path.exists(file):
					os.remove(file)

	def installApp(self):
		reg_file = resource_path("register_protocol.reg")
		self.save_reg_file(self.create_reg_install(), reg_file)
		os.startfile(reg_file)

	def uninstallApp(self):
		reg_file = resource_path("uninstall.reg")
		self.save_reg_file(self.create_reg_uninstall(), reg_file)
		os.startfile(reg_file)

	def create_reg_install(self):
		app_path = self.master.appConfig['app_path'].replace("\\", "\\\\")

		reg_content = f"""Windows Registry Editor Version 5.00

		[HKEY_CLASSES_ROOT\\{self.protocol}]
		@="URL:{self.protocol} Protocol"
		"URL Protocol"=""

		[HKEY_CLASSES_ROOT\\{self.protocol}\\shell]

		[HKEY_CLASSES_ROOT\\{self.protocol}\\shell\\open]

		[HKEY_CLASSES_ROOT\\{self.protocol}\\shell\\open\\command]"""
		if self.master.appConfig['run_as'] == "exe":
			reg_content+= f"""
		@="\\"{app_path}\\" \\"-browser\\" \\"%1\\""
			"""
		else:
			python_path = self.master.appConfig['python_path'].replace("\\", "\\\\")
			reg_content+= f"""
		@="\\"{python_path}\\" \\"{app_path}\\" \\"-browser\\" \\"%1\\""
			"""

		return reg_content

	def create_reg_uninstall(self):
		reg_content = f"""Windows Registry Editor Version 5.00

		[-HKEY_CLASSES_ROOT\\{self.protocol}]
		"""
		return reg_content

	def save_reg_file(self, reg_content, file_path):
		with open(file_path, 'w', encoding='utf-8') as reg_file:
			reg_file.write(reg_content)
