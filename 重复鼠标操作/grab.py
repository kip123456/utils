from pynput.keyboard import Listener
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key

from PIL import ImageGrab
from enum import Enum
import pickle
import time
import os
import signal

import ctypes




class Status(Enum):
    NOTHING = 0
    SHORT_INTERVAL = 1
    LONG_INTERVAL = 2

status = Status.NOTHING
command_queue = []
cache = None

default_interval = 1

def grab_color_position():
    mouse_controller = MouseController()
    x,y = mouse_controller.position
    position = mouse_controller.position
    print(f"mouse position: {position}")
    left,top = x-3,y-3
    right, bottom = x-2,y-2
    # 截取屏幕对应区域
    screen = ImageGrab.grab(bbox=(left, top, right, bottom))

    # 获取所有像素
    pixels = screen.load()
    # 遍历获取像素颜色
    colors = []
    for i in range(screen.width):
        for j in range(screen.height):
            colors.append(pixels[i, j])
            assert colors[-1] == colors[0]
    assert len(colors)>0
    return (colors[0], position)

def on_press(key):
    global status
    global command_queue
    global cache
    
    mouse_controller = MouseController()
    
    strkey = str(key)
    if strkey[0] == '\'' and strkey[-1] == '\'':
        strkey = strkey[1:-1]
    print(f"strkey {strkey} pressed")
    if strkey == "q":
        print("监听结束")
        return False
    elif strkey == "s":
        assert status == Status.NOTHING
        print("short interval begin")
        status = Status.SHORT_INTERVAL
        cache = 0
    elif strkey == "l":
        assert status == Status.NOTHING or status == Status.LONG_INTERVAL
        
        if status == Status.LONG_INTERVAL:
            print("long interval end")
            status = Status.NOTHING
            command_queue.append(("l", cache))
        else:
            print("long interval begin")
            status = Status.LONG_INTERVAL
            cache = 0
    elif strkey.isdigit():
        assert status == Status.SHORT_INTERVAL or status == Status.LONG_INTERVAL
        cache = cache * 10 + int(strkey)
        if status == Status.SHORT_INTERVAL:
            print("short interval end")
            status = Status.NOTHING
            command_queue.append(("s", cache))
        else:
            print("in long interval")
    elif strkey == "g":
        print("grabing color around mouse and will be check")
        command_queue.append(("g", grab_color_position()))
    elif strkey == "c":
        print("should click")
        command_queue.append(("c", mouse_controller.position))
    elif strkey == "e":
        print("should enter")
        command_queue.append(("e",))
    elif strkey == "]":
        print("should ]")
        command_queue.append(("]",))
    
    else:
        print("invalid key")

def on_exit_press(key):
    if str(key) == "q":
        os.kill(os.getpid(), signal.SIGTERM)

def exec_command_queue(command_queue):
    global default_interval
    mouse_controller = MouseController()
    keyboard_controller = KeyboardController()
    print("starting exec_command_queue")
    
    for c in command_queue:
        print(f"exec command {c}")
        if c[0]!="s" and c[0] != "l":
            print(f"default sleeping {default_interval}s")
            time.sleep(default_interval)
        if c[0] == "s" or c[0] == "1":
            print(f"sleeping {c[1]}s")
            time.sleep(c[1])
        elif c[0] == "g":
            color, pos = c[1]
            mouse_controller.position = pos
            while True:
                time.sleep(default_interval)
                nc, _ = grab_color_position()
                if nc == color:
                    break
        elif c[0] == "c":
            mouse_controller.position = c[1]
            mouse_controller.click(Button.left)
        elif c[0] == "e":
            keyboard_controller.press(Key.enter)
            keyboard_controller.release(Key.enter)
        elif c[0] == "]":
            keyboard_controller.press("]")
            keyboard_controller.release("]")
        else:
            raise Exception("Invalid Operation")
        
        
    
    print("ending exec_command_queue")
        
        
if __name__ == "__main__":
    
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)


    
    print("input 1 to record")
    print("input 2 to exec")
    print("others to exit")
    
    while True:
        x = int(input())
        if x == 1:
            print("input name to record:")
            name = input()
            command_queue = []
            with Listener(on_press=on_press) as lis:
                lis.join()
            filename = name + ".pkl"
            print("command_queue")
            print(command_queue)
            with open(filename, "wb") as f:
                pickle.dump(command_queue, f)
        elif x == 2:
            print("input name to resolve")
            name = input()
            filename = name + ".pkl"
            with open(filename, "rb") as f:
                command_queue = pickle.load(f)
            with Listener(on_press=on_exit_press) as lis:
                while True:
                    exec_command_queue(command_queue)
                lis.join()
            
            















# def on_press(key):
#     print(f"pressed key {key}")
    
# with Listener(on_press=on_press) as lis:
#     lis.join