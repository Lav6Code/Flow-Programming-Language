import tkinter as tk
from tkinter.filedialog import *
import sv_ttk
import importlib.util
import sys
import os
import subprocess
import threading
import queue
from pathlib import Path


# Interactive Console Definition
class InteractiveConsole(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, font=("Consolas", 11), height=17, width=37)
        self.text.pack(expand=True, fill=tk.BOTH)
        self.text.bind("<Return>", self.on_enter)
        self.text.configure(state="disabled")

        self.process = None
        self.input_queue = queue.Queue()

    def start_process(self, command):
        """Starts a subprocess with the specified command."""
        if self.process is not None and self.process.poll() is None:
            self.text.insert(tk.END, "A process is already running.\n")
            return

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"Flow executing: {file.name.split("/")[-1]}\n")
        self.text.see(tk.END)
        

        threading.Thread(target=self.read_output, daemon=True).start()

    def read_output(self):
        global VARS
        VARS = {}
        """Reads utput from the subprocess."""
        for line in iter(self.process.stdout.readline, ""):
            if line.startswith(VARS_CONNECTION_KEY+"{"):
                dicts = line[len(VARS_CONNECTION_KEY):-1]
                dicts.split(",")
                VARS = eval(dicts)
                update_variables_textbox(VARS)
            else:
                self.text.insert(tk.END, line)
                self.text.see(tk.END)
        self.text.insert(tk.END, f"{file.name.split("/")[-1]} is executed.\n {"_"*terminal.cget("width")}")
        self.text.see(tk.END)
        self.text.configure(state="disabled")

    def on_enter(self, event):
        """Handles the Enter key press for sending input."""
        if self.process is None or self.process.poll() is not None:
            self.text.insert(tk.END, "\nNo process running.\n")
            return "break"

        line = self.text.get("insert linestart", "insert").strip()
        self.text.insert(tk.END, "\n")  # Move to a new line
        self.text.see(tk.END)

        if line:
            self.process.stdin.write(line + "\n")
            self.process.stdin.flush()

        return "break"


# SETUP
WIDTH, HEIGHT = 1207, 800
app = tk.Tk()
app.geometry(str(WIDTH) + "x" + str(HEIGHT))
app.lift()
app.title("untitled.flow")
app.resizable(True, True)

# FLOW SETUP
green_keywords = ['+', '*', "-", "/"]
red_keywords = ['var', 'output', "input", "if", "for", "while", "fetch", "intersection", "union", "disjunction", "superset", "subset", "len"]
orange_keywords = ["1", "2", "3", "3", "4", "5", "6", "7", "8", "9", "0", '"']
blue_keywords = [";", "(", ")"]
flow_path = "C:/Users/Valchichi/Dropbox/PROGRAMIRANJE/FLOW-programming language/FLOW.py"


# FUNCTIONS (Unchanged from your original implementation)
def update_variables_textbox(variables):
    print(variables)
    global variable_box
    variable_box.config(state="normal")
    variable_box.delete("1.0", tk.END)
    insert_text = ""
    
    for v in variables:
        insert_text += f"{v}={variables[v]}\n"
    variable_box.insert("1.0",insert_text)
    variable_box.config(state="disabled")

def highlight(keyword, tag_name):
    start = "1.0"
    while True:
        pos = textbox.search(keyword, start, stopindex=tk.END)
        end = f"{pos}+{len(keyword)}c"
        start = end
        if not pos:
            break
        if keyword == textbox.get(pos, end):
            textbox.tag_add(tag_name, pos, end)


def update_line_counter():
    global line_counter
    n = textbox.get("1.0", tk.END).count("\n")
    text = ""
    for i in range(n):
        text += f"{i + 1}.\n"

    line_counter.config(state="normal")
    line_counter.delete('1.0', tk.END)
    line_counter.insert("1.0", text)
    line_counter.config(state="disabled")


def update_text(a=None):
    global line_counter
    textbox.tag_remove("GREEN", 1.0, tk.END)
    textbox.tag_remove("RED", 1.0, tk.END)
    textbox.tag_remove("BLUE", 1.0, tk.END)

    for word in green_keywords:
        highlight(word, "GREEN")
    for word in red_keywords:
        highlight(word, "RED")
    for word in blue_keywords:
        highlight(word, "BLUE")
    for word in orange_keywords:
        highlight(word, "ORANGE")

    bucket = ""
    inside_n = []
    n_counter = 0
    for l in textbox.get("1.0", tk.END):
        if l == '"':
            n_counter += 1
            if n_counter == 2:
                n_counter = 0

        if n_counter == 1:
            bucket += l
        else:
            if bucket != "":
                inside_n.append(bucket)
                bucket = ""

    for word in inside_n:
        highlight(word, "ORANGE")

    update_line_counter()


def auto_finish(event=None):
    char_mapping = {"(": ")", '"': '"', "[": "]", "{": "}"}
    if event.char in char_mapping.keys():
        current_position = textbox.index(tk.INSERT)
        textbox.insert(current_position, char_mapping[event.char])
        textbox.mark_set(tk.INSERT, current_position)

    update_text()


def focus_text_widget():
    textbox.focus_force()

def new_file(event=None):
    global file
    response = tk.messagebox.askquestion(title="⚠️ File will not be saved! ⚠️",
                                             message="Save file before opening another file?", type="yesnocancel")
    if response == "yes":
        save_file()
        textbox.delete("1.0", tk.END)
        app.update()
    elif response == "cancel":
        ...
    else:
        textbox.delete("1.0", tk.END)
        app.update()
    file = None
    app.title("Untitled.flow")

def open_file(event=None):
    global file
    if textbox.get("1.0", tk.END).replace("\n", "") == "":
        file = askopenfile(mode='r', filetypes=[('Flow Files', '*.flow')])
        if file is not None:
            file_content = file.read()
            textbox.delete("1.0", tk.END)
            textbox.insert(tk.INSERT, file_content[:-1])
            update_text()
    else:
        response = tk.messagebox.askquestion(title="⚠️ File will not be saved! ⚠️",
                                             message="Save file before opening another file?", type="yesnocancel")
        if response == "yes":
            save_file()
            textbox.delete("1.0", tk.END)
            app.update()
            open_file()
        elif response == "cancel":
            pass
        else:
            textbox.delete("1.0", tk.END)
            app.update()
            open_file()

    if file is not None:
        app.title(file.name.split("/")[-1])
    else:
        app.title("untitled.flow")


def save_file(event=None):
    global file

    if file:
        with open(file.name, 'a') as f:
            f.truncate(0)
            f.write(textbox.get("1.0", tk.END))
            file.close()
    else:
        file = asksaveasfile(defaultextension=".flow", filetypes=[("Flow files", "*.flow")])
        if file:
            app.title(file.name.split("/")[-1])
            file.write(textbox.get("1.0", tk.END))
            file.close()


def run_file(event=None):
    global terminal, flow_path, file
    save_file()
    if file:
        terminal.start_process(["python", os.path.normpath(flow_path), os.path.normpath(file.name)])

def exita(event=None):
    sys.exit()

#Setting file to NONE
file=None

# WIDGETS (Same as original code, except terminal replaced)
textbox = tk.Text(app, width=57, height=23, font=("Consolas 20"), undo=True)
textbox.place(rely=0, relx=0.04)
textbox.tag_config("GREEN", foreground="green")
textbox.tag_config("RED", foreground="red")
textbox.tag_config("ORANGE", foreground="orange")
textbox.tag_config("BLUE", foreground="lightblue")
textbox.config(spacing1=10)

variable_box = tk.Text(app, width=20, height=10, font=("Consolas 20"))
variable_box.place(rely=0.082, relx=0.75171)
variable_box.config(state="disabled")

variable_label = tk.Label(app, text="║VARIABLES║\n╚=========╝", font=("Consolas 20"), fg="lightblue")
variable_label.place(relx=0.81, rely=-0)

VARS_CONNECTION_KEY = "152693"

line_counter = tk.Text(app, width=3, height=23, font=("Consolas 20"), fg="lightblue", state="disabled")
line_counter.place(rely=-0, relx=0)
line_counter.config(spacing1=10)

# Replace the tkterminal with the new InteractiveConsole
terminal = InteractiveConsole(app)
terminal.place(relx=0.751, rely=0.6)

console_label = tk.Label(app, text="║ CONSOLE ║\n╚=========╝", font=("Consolas 20"), fg="lightblue")
console_label.place(relx=0.81, rely=0.5)

# MENU BAR (Unchanged)
menubar = tk.Menu()
file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(label="New", accelerator="Ctrl+N", command=new_file)
file_menu.add_command(label="Open", accelerator="Ctrl+O", command=open_file)
file_menu.add_command(label="Save", accelerator="Ctrl+S", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", accelerator="Ctrl+E", command=exit)
menubar.add_cascade(menu=file_menu, label="File")

run_menu = tk.Menu(menubar, tearoff=False)
run_menu.add_command(label="Run", accelerator="F5", command=run_file)
menubar.add_cascade(menu=run_menu, label="Run")
app.config(menu=menubar)

# Bindings (Unchanged)
app.bind("<Control-n>", new_file)
app.bind("<Control-o>", open_file)
app.bind("<Control-s>", save_file)
app.bind("<Control-e>", exit)
app.bind("<F5>", run_file)
app.bind_all('<Key>', update_text)

# THEME AND MAIN LOOP
sv_ttk.set_theme("dark")
app.mainloop()
