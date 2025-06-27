def register_file_association():
    pass

def main():
    #命令行参数解析
    parser = argparse.ArgumentParser(description="文本编辑器")
    parser.add_argument("file",  nargs="?", help="要打开的.text文件")
    parser.add_argument("--register",  action="store_true", help="注册.text文件关联")
    args = parser.parse_args()
    if args.register:
        if (sys.platform == 'win32'):
            #Windows平台需要管理员权限
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                register_file_association()
                #尝试以管理员权限重新运行
            else :
                ctypes.windll.shell32.ShellExecuteW(None,  "runas", sys.executable,  " ".join(sys.argv),  None, 1)
        else :
            messagebox.showinfo(" 提示", "文件关联功能仅支持Windows系统")
        return
    #启动GUI界面
    root = tk.Tk()
    editor = TextEditor(root)
    #如果通过命令行指定了文件，直接打开
    if args.file:
        editor.open_file(args.file)
    root.mainloop()


import os
import sys
import tkinter as tk

import winreg
import argparse
import webbrowser
import platform
from datetime import datetime

#版本信息
VERSION = '1.1.0'
RELEASE_DATE = '2025-06-27'
DEVELOPER = 'Michaelsoft Community'
HELP_URL = 'https://laptop-afk.github.io/text-editor.html'
GITHUB_URL = 'https://github.com/LAPTOP-afk/text-editor'

class TextEditor:
    def __init__(self, root):
        self.root  = root
        self.root.title("Text  Editor")
        self.root.geometry("800x600")

        # 创建菜单栏
        self.menu_bar  = tk.Menu(root)

        # 文件菜单
        self.file_menu  = tk.Menu(self.menu_bar,  tearoff=0)
        self.file_menu.add_command(label=" 新建", command=self.new_file,  accelerator="Ctrl+N")
        self.file_menu.add_command(label=" 打开", command=self.open_file,  accelerator="Ctrl+O")
        self.file_menu.add_command(label=" 保存", command=self.save_file,  accelerator="Ctrl+S")
        self.file_menu.add_command(label=" 另存为", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=" 退出", command=self.exit_app)
        self.menu_bar.add_cascade(label=" 文件", menu=self.file_menu)

        # === 新增编辑菜单 ===
        self.edit_menu  = tk.Menu(self.menu_bar,  tearoff=0)
        self.edit_menu.add_command(label=" 剪切", command=self.cut_text,  accelerator="Ctrl+X")
        self.edit_menu.add_command(label=" 复制", command=self.copy_text,  accelerator="Ctrl+C")
        self.edit_menu.add_command(label=" 粘贴", command=self.paste_text,  accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label=" 全选", command=self.select_all,  accelerator="Ctrl+A")
        self.edit_menu.add_command(label=" 删除", command=self.delete_text,  accelerator="Del")
        self.menu_bar.add_cascade(label=" 编辑", menu=self.edit_menu)
        # === 编辑菜单结束 ===

        # 帮助菜单
        self.help_menu  = tk.Menu(self.menu_bar,  tearoff=0)
        self.help_menu.add_command(label=" 获取帮助", command=self.open_help)
        self.help_menu.add_command(label=" 关于", command=self.show_about)
        self.menu_bar.add_cascade(label=" 帮助", menu=self.help_menu)

        # 注册快捷键
        self.root.bind('<Control-n>',  lambda event: self.new_file())
        self.root.bind('<Control-o>',  lambda event: self.open_file())
        self.root.bind('<Control-s>',  lambda event: self.save_file())
        # === 新增编辑快捷键 ===
        self.root.bind('<Control-x>',  lambda event: self.cut_text())
        self.root.bind('<Control-c>',  lambda event: self.copy_text())
        self.root.bind('<Control-v>',  lambda event: self.paste_text())
        self.root.bind('<Control-a>',  lambda event: self.select_all())
        self.root.bind('<Delete>',  lambda event: self.delete_text())

        # 创建文本编辑区域
        self.text_area  = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH,  expand=True)

        # 状态栏
        self.status_bar  = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM,  fill=tk.X)

        self.root.config(menu=self.menu_bar)
        self.current_file  = None

    # === 新增编辑功能方法 ===
    def cut_text(self):
        """剪切选中的文本"""
        self.text_area.event_generate("<<Cut>>")
        self.update_status(" 已剪切选中文本")

    def copy_text(self):
        """复制选中的文本"""
        self.text_area.event_generate("<<Copy>>")
        self.update_status(" 已复制选中文本")

    def paste_text(self):
        """在光标处粘贴文本"""
        self.text_area.event_generate("<<Paste>>")
        self.update_status(" 已粘贴文本")

    def select_all(self):
        """全选文本"""
        self.text_area.tag_add(tk.SEL,  "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT,  "1.0")
        self.text_area.see(tk.INSERT)
        self.update_status(" 已全选文本")

    def delete_text(self):
        """删除选中的文本"""
        if self.text_area.tag_ranges(tk.SEL):
            self.text_area.delete(tk.SEL_FIRST,  tk.SEL_LAST)
        self.update_status(" 已删除选中文本")

    def new_file(self):
        self.text_area.delete(1.0,  tk.END)
        self.current_file  = None
        self.update_status(" 新建文件")

    def open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.text"), ("All files", "*.*")]
            )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.delete(1.0,  tk.END)
                    self.text_area.insert(tk.INSERT,  file.read())
                self.current_file  = file_path
                self.root.title(f"Text  Editor - {os.path.basename(file_path)}")
                self.update_status(f" 已打开: {file_path}")
            except Exception as e:
                messagebox.showerror(" 错误", f"无法打开文件:\n{str(e)}")

    def save_file(self):
        if not self.current_file:
            self.save_as_file()
        else:
            try:
                with open(self.current_file,  'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0,  tk.END))
                self.update_status(f" 已保存: {self.current_file}")
            except Exception as e:
                messagebox.showerror(" 错误", f"保存失败:\n{str(e)}")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".text",
            filetypes=[("Text files", "*.text"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0,  tk.END))
                self.current_file  = file_path
                self.root.title(f"Text  Editor - {os.path.basename(file_path)}")
                self.update_status(f" 已另存为: {file_path}")
            except Exception as e:
                messagebox.showerror(" 错误", f"保存失败:\n{str(e)}")

    def update_status(self, message):
        self.status_bar.config(text=message)

    def exit_app(self):
        self.root.destroy()

    # 帮助菜单功能
    def open_help(self):
        webbrowser.open(HELP_URL)
        self.update_status(" 已打开帮助页面")

    def show_about(self):
        about_info = (
            f"文本编辑器 v{VERSION}\n"
            f"发布日期: {RELEASE_DATE}\n"
            f"开发者: {DEVELOPER}\n"
            f"Python版本: {platform.python_version()}\n"
            f"系统平台: {platform.system()}  {platform.release()}\n"
            f"GitHub: {GITHUB_URL}"
        )
        messagebox.showinfo(" 关于", about_info)
        self.update_status(" 显示关于信息")

#创建菜单栏

#文件菜单

#=== 新增编辑菜单 ===

#=== 编辑菜单结束 ===

#帮助菜单

#注册快捷键

#=== 新增编辑快捷键 ===

#创建文本编辑区域

#状态栏

#=== 新增编辑功能方法 ===

#帮助菜单功能

'注册.text文件后缀关联到当前程序'

try:
    #获取当前程序路径
    exe_path = os.path.abspath(sys.argv[0])
    #创建文件类型注册表项
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".text") as key:
    #创建关联命令
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TextEditorFile\shell\open\command") as key:
    #添加右键菜单项
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TextEditorFile\shell\copypath") as key:
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TextEditorFile\shell\copypath\command") as key:
    messagebox.showinfo(" 注册成功", ".text文件后缀已成功关联到本程序")
    return True
except PermissionError:
    messagebox.showerror(" 权限错误", "需要管理员权限运行才能注册文件关联")
    return False
except Exception:
    messagebox.showerror(" 错误", f"注册失败:\n{str(e)}")
    return False

if (__name__ == '__main__'):
    main()
