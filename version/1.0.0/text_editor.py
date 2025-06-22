import os
import sys 
import tkinter as tk 
from tkinter import filedialog, messagebox, scrolledtext 
import winreg
import argparse 
import webbrowser
import platform 
from datetime import datetime
 
# 版本信息
VERSION = "1.0.0"
RELEASE_DATE = "2025-06-22"
DEVELOPER = "Michaelsoft Community"
HELP_URL = "https://LAPTOP-afk.github.io/text-editor.html" 
GITHUB_URL = "https://github.com/LAPTOP-afk/text-editor" 
 
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
        self.file_menu.add_command(label=" 另存为", command=self.save_as_file,  accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator() 
        self.file_menu.add_command(label=" 退出", command=self.exit_app) 
        self.menu_bar.add_cascade(label=" 文件", menu=self.file_menu) 
        
        # 新增帮助菜单 
        self.help_menu  = tk.Menu(self.menu_bar,  tearoff=0)
        self.help_menu.add_command(label=" 获取帮助", command=self.open_help) 
        self.help_menu.add_command(label=" 关于", command=self.show_about) 
        self.menu_bar.add_cascade(label=" 帮助", menu=self.help_menu) 
        
        # 注册快捷键 
        self.root.bind('<Control-n>',  lambda event: self.new_file()) 
        self.root.bind('<Control-o>',  lambda event: self.open_file()) 
        self.root.bind('<Control-s>',  lambda event: self.save_file()) 
        self.root.bind('<Control-Shift-S>',  lambda event: self.save_as_file()) 
        
        # 创建文本编辑区域 
        self.text_area  = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11))
        self.text_area.pack(fill=tk.BOTH,  expand=True)
        
        # 状态栏
        self.status_bar  = tk.Label(root, text="就绪 - 字符数: 0 | 行数: 1", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5)
        self.status_bar.pack(side=tk.BOTTOM,  fill=tk.X)
        
        # 绑定文本变化事件 
        self.text_area.bind('<KeyRelease>',  self.update_status) 
        
        self.root.config(menu=self.menu_bar) 
        self.current_file  = None 
        self.update_status() 
        
        # 设置程序图标（可选）
        try:
            self.root.iconbitmap("text_editor.ico") 
        except:
            pass
 
    def new_file(self):
        self.text_area.delete(1.0,  tk.END)
        self.current_file  = None 
        self.root.title("Text  Editor")
        self.update_status(" 新建文件")
 
    def open_file(self, file_path=None, event=None):
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
 
    def save_file(self, event=None):
        if not self.current_file: 
            self.save_as_file() 
        else:
            try:
                with open(self.current_file,  'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0,  tk.END))
                self.update_status(f" 已保存: {self.current_file}") 
            except Exception as e:
                messagebox.showerror(" 错误", f"保存失败:\n{str(e)}")
 
    def save_as_file(self, event=None):
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
 
    def update_status(self, event=None):
        """更新状态栏信息"""
        content = self.text_area.get(1.0,  tk.END)
        char_count = len(content) - 1  # 减去末尾的换行符 
        line_count = int(self.text_area.index(tk.END).split('.')[0])  - 1 
        
        file_info = f" - {os.path.basename(self.current_file)}"  if self.current_file  else ""
        status_text = f"字符数: {char_count} | 行数: {line_count}{file_info}"
        self.status_bar.config(text=status_text) 
 
    def exit_app(self):
        if messagebox.askokcancel(" 退出", "确定要退出程序吗？"):
            self.root.destroy() 
 
    def open_help(self):
        """打开帮助网站"""
        webbrowser.open(HELP_URL) 
        self.update_status(f" 已打开帮助页面: {HELP_URL}")
 
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""文本编辑器 {VERSION}
 
一个轻量级的文本编辑工具，支持.text文件格式
 
发布日期: {RELEASE_DATE}
开发者: {DEVELOPER}
操作系统: {platform.system()}  {platform.release()} 
 
功能特点:
✓ 支持.text文件格式注册 
✓ UTF-8编码支持 
✓ 响应式用户界面
✓ 实时字符计数 
 
项目主页: {GITHUB_URL}"""
 
        messagebox.showinfo(" 关于文本编辑器", about_text)
 
def register_file_association():
    """注册.text文件后缀关联到当前程序"""
    try:
        # 获取当前程序路径 
        exe_path = os.path.abspath(sys.argv[0]) 
        
        # 创建文件类型注册表项 
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".text") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "TextEditorFile")
            winreg.SetValueEx(key, "Content Type", 0, winreg.REG_SZ, "text/plain")
            winreg.SetValueEx(key, "PerceivedType", 0, winreg.REG_SZ, "text")
        
        # 创建文件类型描述 
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "TextEditorFile") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "文本文档")
        
        # 创建默认图标 
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TextEditorFile\DefaultIcon") as key:
            # 使用系统默认文本图标 
            winreg.SetValue(key, "", winreg.REG_SZ, r"%SystemRoot%\system32\imageres.dll,-102") 
        
        # 创建关联命令 
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"TextEditorFile\shell\open\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{sys.executable}"  "{exe_path}" "%1"')
        
        messagebox.showinfo(" 注册成功", ".text文件后缀已成功关联到本程序")
        return True
    except PermissionError:
        messagebox.showerror(" 权限错误", "需要管理员权限运行才能注册文件关联")
        return False 
    except Exception as e:
        messagebox.showerror(" 错误", f"注册失败:\n{str(e)}")
        return False 
 
def force_admin_registration():
    """请求管理员权限进行注册"""
    try:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin(): 
            return register_file_association()
        else:
            ctypes.windll.shell32.ShellExecuteW(None,  "runas", sys.executable,  " ".join(sys.argv),  None, 1)
            return True 
    except:
        return False
 
def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="文本编辑器")
    parser.add_argument("file",  nargs="?", help="要打开的.text文件")
    parser.add_argument("--register",  action="store_true", help="注册.text文件关联")
    parser.add_argument("--version",  action="store_true", help="显示版本信息")
    args = parser.parse_args() 
 
    if args.version: 
        print(f"文本编辑器 {VERSION} ({RELEASE_DATE})")
        return 
 
    if args.register: 
        if sys.platform  == "win32":
            # 尝试以管理员权限注册
            force_admin_registration()
        else:
            messagebox.showinfo(" 提示", "文件关联功能仅支持Windows操作系统")
        return 
 
    # 启动GUI界面
    root = tk.Tk()
    editor = TextEditor(root)
    
    # 如果通过命令行指定了文件，直接打开
    if args.file: 
        editor.open_file(args.file) 
    
    root.mainloop() 
 
if __name__ == "__main__":
    main()