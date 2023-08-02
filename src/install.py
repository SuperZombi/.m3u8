import os
import sys

def create_reg_install(protocol, app_path):
    app_path = app_path.replace("\\", "\\\\")
    python_path = sys.executable.replace("\\", "\\\\")
    reg_content = f"""Windows Registry Editor Version 5.00

    [HKEY_CLASSES_ROOT\\{protocol}]
    @="URL:{protocol} Protocol"
    "URL Protocol"=""

    [HKEY_CLASSES_ROOT\\{protocol}\\shell]

    [HKEY_CLASSES_ROOT\\{protocol}\\shell\\open]

    [HKEY_CLASSES_ROOT\\{protocol}\\shell\\open\\command]
    @="\\"{python_path}\\" \\"{app_path}\\" \\"-browser\\" \\"%1\\""
    """
    return reg_content

def create_reg_uninstall(protocol):
    reg_content = f"""Windows Registry Editor Version 5.00

    [-HKEY_CLASSES_ROOT\\{protocol}]
    """
    return reg_content

def save_reg_file(reg_content, file_path):
    with open(file_path, 'w', encoding='utf-8') as reg_file:
        reg_file.write(reg_content)

if __name__ == "__main__":
    os.system("cls")
    print("            M3U8 Installer")
    protocol = "m3u8"
    after_work = []

    print("1 - Install application to registry\n2 - Remove application from registry")
    choice = input("> ")
    if choice == "1":
        # Install
        app_path = os.path.join(os.getcwd(), "downloader.py")
        if not os.path.exists(app_path):
            print(f"Error: app file not found ({app_path})")
        else:
            print(f"Are you sure you want to add to the registry this app:\n{app_path}")
            choice = input("(Y/n) > ")
            if choice.lower() == "y":
                reg_content = create_reg_install(protocol, app_path)
                reg_file = os.path.join(os.getcwd(), "register_protocol.reg")
                save_reg_file(reg_content, reg_file)
                os.startfile(reg_file)
                after_work.append(lambda: os.remove(reg_file) if os.path.exists(reg_file) else None)

    elif choice == "2":
        # Uninstall
        print(f"Are you sure you want to uninstall app from registry?")
        choice = input("(Y/n) > ")
        if choice.lower() == "y":
            reg_content = create_reg_uninstall(protocol)
            reg_file = os.path.join(os.getcwd(), "uninstall.reg")
            save_reg_file(reg_content, reg_file)
            os.startfile(reg_file)
            after_work.append(lambda: os.remove(reg_file) if os.path.exists(reg_file) else None)


    input("Program finished\n")
    for work in after_work:
        work()
