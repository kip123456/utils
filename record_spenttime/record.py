import tkinter as tk
from tkinter import ttk
import datetime
import time

# doing_things是一个字符串数组
doing_things = []

def add_to_log(info:str):
    global logging_filename
    # 向这个文件中添加一行info
    with open(logging_filename.get(), "a") as f:
        f.write(info + "\n")
        f.close()
def add_task():
    global doing_things, listbox, entry
    task = entry.get()
    if task:
        doing_things.append(task)
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)  # 清空输入框
        add_to_log(f"time {time.time()} push {task}")

def remove_last_task():
    global doing_things, listbox
    if doing_things:
        task=doing_things.pop()
        listbox.delete(tk.END)  # 删除Listbox中的最后一个项
        add_to_log(f"time {time.time()} pop {task}")

def add_today_date():
    global doing_things, listbox
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    task=f"today {today_date}"
    doing_things.append(task)
    listbox.insert(tk.END, task)
    entry.delete(0, tk.END)  # 清空输入框
    add_to_log(f"time {time.time()} push {task}")

def create_gui():
    # 创建主窗口
    global doing_things
    root = tk.Tk()
    root.title("任务列表")
    
    # 创建一个输入框
    global entry
    entry = tk.Entry(root, width=40)
    entry.pack(pady=10)
    
    # 创建另一个输入框来显示并更改全局变量logging_filename的值
    global logging_filename
    logging_filename = tk.StringVar()
    logging_filename_entry = ttk.Entry(root, textvariable=logging_filename)
    logging_filename_entry.pack(pady=10)
    logging_filename.set(f'log_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt')
    # 禁止更改logging_filename
    logging_filename_entry.config(state="readonly")
    
    with open(logging_filename.get(), "w") as f:
        f.close()
    
    
    # 创建一个Listbox来显示doing_things中的内容
    global listbox
    listbox = tk.Listbox(root)
    listbox.pack(pady=20)
    
    # 创建添加任务按钮
    add_button = tk.Button(root, text="添加任务", command=add_task)
    add_button.pack(side=tk.LEFT, padx=10)
    
    # 创建删除任务按钮
    remove_button = tk.Button(root, text="删除最后一个任务", command=remove_last_task)
    remove_button.pack(side=tk.RIGHT, padx=10)

    # 添加一个当gui窗口关闭的回调函数
    def close_callback():
        while doing_things:
            remove_last_task()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", close_callback)
    
    
    add_today_date()
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    create_gui()