import tkinter as tk
from tkinter import filedialog, ttk
import os
from anytree import Node

def analysis(logging_filename: str, treeview: ttk.Treeview):
    # loggging_filename这个文件中的内容形如：
    ## time 1744272313.8912842 push today 2025-04-10
    ## time 1744272320.2228827 push asdfdsf
    ## time 1744272323.621747 pop asdfdsf
    ## time 1744272323.621747 pop today 2025-04-10
    # 将其解析为(float, str str)这种形式，比如(1744272313.8912842, "push", "today 2025-04-10")
    
    things_stack = []
    nodes = []
    
    with open(logging_filename, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        split_line = line.split(" ")
        this_time = float(split_line[1])
        action = split_line[2]
        # task 的值为split_line[3:]这个列表合并起来，中间添加空格
        task = " ".join(split_line[3:])
        action = action.strip()
        task = task.strip()
        # print(time, action, task)
        assert action == "push" or action == "pop"
        
        if action == "push":
            id = len(nodes)
            nodes.append((id, task, this_time))
            things_stack.append((id, task, this_time))
            
        else:
            thing = things_stack.pop()
            assert task == thing[1]
            id = thing[0]
            start_time = thing[2]
            assert start_time == nodes[id][2]
            if things_stack:
                parent = things_stack[len(things_stack) - 1][0]
            else:
                parent = -1
            nodes[id] = (id, task, this_time - start_time, parent)
    
    # 用anytree把nodes展示出来
    node_dict = {}
    for node in nodes:
        id, task, duration, parent_id = node
        if parent_id == -1:
            node_dict[id] = Node(f"{id} {task} ({duration:.2f}s)")
        else:
            node_dict[id] = Node(f"{id} {task} ({duration:.2f}s)", parent=node_dict[parent_id])
    
    # 清空当前的Treeview
    for item in treeview.get_children():
        treeview.delete(item)
    
    # 插入节点到Treeview
    def insert_node(node, parent=''):
        treeview.insert(parent, 'end', iid=str(node.name), text=node.name)
        for child in node.children:
            insert_node(child, str(node.name))
    
    if node_dict:
        root_node = next(iter(node_dict.values()))
        insert_node(root_node)

def create_gui():
    def select_file():
        # 弹出文件选择对话框，初始位置是程序所在的文件夹
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="选择文件",
                                             filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*")))
        if filename:
            loggin_filename.delete(0, tk.END)
            loggin_filename.insert(0, filename)

    def analyze_and_display():
        filename = loggin_filename.get()
        if filename:
            analysis(filename, treeview)

    # 创建主窗口
    root = tk.Tk()
    # 窗口设置大一点
    root.geometry("600x400")
    root.title("简单GUI示例")

    # 创建输入框
    loggin_filename = tk.Entry(root, width=60)
    loggin_filename.pack(expand=True, fill=tk.BOTH, pady=10)

    # 创建文件选择按钮
    file_button = tk.Button(root, text="选择文件", command=select_file)
    file_button.pack(side=tk.LEFT, padx=5, pady=10)

    # 创建一个按钮
    analyze_button = tk.Button(root, text="分析", command=analyze_and_display)
    analyze_button.pack(side=tk.RIGHT, pady=10)

    # 创建Treeview控件
    treeview = ttk.Treeview(root)
    treeview.pack(expand=True, fill=tk.BOTH, pady=10)

    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    create_gui()