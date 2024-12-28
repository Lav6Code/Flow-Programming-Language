import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import *
import importlib.util
import sys
import os
os.system("")
import subprocess
import threading
import queue
from pathlib import Path
import sv_ttk

# Interactive Console Definition
class InteractiveConsole(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, font=("Consolas", 11), height=16, width=37)
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
        self.text.configure(state="normal")
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        self.text.insert(tk.END, f"EXECUTING: {file.split('/')[-1]}\n{'═'*37}\n")
        self.text.see(tk.END)

        threading.Thread(target=self.read_output, daemon=True).start()

    def read_output(self):
        """Reads utput from the subprocess."""
        for line in iter(self.process.stdout.readline, ""):
            if line.startswith(VARS_CONNECTION_KEY+"{"): # { beacuse its a dictionary, just for safety purposes
                dicts = line[len(VARS_CONNECTION_KEY):-1]
                dicts.split(",")
                VARS = eval(dicts)
                update_variables_textbox(VARS)

            elif line.startswith(FUNS_CONNECTION_KEY):
                dicts = line[len(FUNS_CONNECTION_KEY):-1]
                dicts.split(",")
                FUNS = eval(dicts)
                update_functions_textbox(FUNS)

            else:
                self.text.insert(tk.END, line)
                self.text.see(tk.END)
        self.text.see(tk.END)
        self.text.insert(tk.END,'═'*37, "\n")

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
WIDTH, HEIGHT = 1207, 700
app = tk.Tk()
app.geometry(str(WIDTH) + "x" + str(HEIGHT))
app.lift()
app.title("untitled.flow")
app.resizable(True, True)

# FLOW SETUP
green_keywords = ['+', '*', "-", "/"]
red_keywords = ['var', 'output', "input", "if", "for", "while", "fetch", "intersection", "union", "disjunction", "superset", "subset", "len"]
orange_keywords = ["1", "2", "3", "3", "4", "5", "6", "7", "8", "9", "0", '"', "num", "set"]
blue_keywords = [";", "(", ")"]
purple_keywords = ["$"] # COMMENT

# FLOW path
flow_path = "./FLOW.py"


# FUNCTIONS (Unchanged from your original implementation)
def change_path_f():
    global flow_path, intpreter_configuration_window
    
    flow_file = askopenfile(title="Select Flow Intpereter", mode ='r', filetypes =[('Python', '*.py')])
    if flow_file is not None:
        flow_path = flow_file.name
    else:
        flow_path = None
    intpreter_configuration_window.destroy()

def interpreter_configuration(event=None):
    global intpreter_configuration_window
    intpreter_configuration_window = tk.Toplevel(app)
    intpreter_configuration_window.geometry("750x150")
    intpreter_configuration_window.title("Configure Intepreter")
    intpreter_configuration_window.after(10, intpreter_configuration_window.lift)
    
    current_intepreter_title = tk.Label(master=intpreter_configuration_window, text="╔{ CURRENT INTEPRETER }╗", fg="#3277a8", font = ("Calibri Bold", 16))
    current_intepreter_title.pack()
    
    current_path = tk.Label(master=intpreter_configuration_window, text="", font = "Consolas 12", bg = "#8f99a1", fg = "#000")
    if flow_path:
        current_path.config(text=flow_path)
    else:
        current_path.config(text="⚠️NO INTEPRETER SELECTED⚠️")
    current_path.pack()
    
    change_path = tk.Button(intpreter_configuration_window, text="Change Path to FLOW intepreter", command = change_path_f)
    change_path.place(relx=0.5,rely=0.7, anchor=tk.CENTER)
    
def update_variables_textbox(variables):
    global variable_box
    variable_box.config(state="normal")
    variable_box.delete("1.0", tk.END)
    insert_text = ""
    
    for v in variables:
        if type(variables[v]) == int:
            insert_text += f"{v}={variables[v]}\n"
        elif type(variables[v]) == str:
            insert_text += f"{v}='{variables[v]}'\n"

    variable_box.insert("1.0",insert_text)
    variable_box.config(state="disabled")

def update_functions_textbox(functions):
    global function_box
    function_box.config(state="normal")
    function_box.delete("1.0", tk.END)
    insert_text = ""
    print(functions)
    
    for v in functions:
        insert_text += (v + "\n")

    function_box.insert("1.0",insert_text)
    function_box.config(state="disabled")

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
    textbox.tag_remove("ORANGE", 1.0, tk.END)
    textbox.tag_remove("PURPLE", 1.0, tk.END)

    for word in green_keywords:
        highlight(word, "GREEN")
    for word in red_keywords:
        highlight(word, "RED")
    for word in blue_keywords:
        highlight(word, "BLUE")
    for word in orange_keywords:
        highlight(word, "ORANGE")
    for word in purple_keywords:
        highlight(word, "PURPLE")

    # WORDS INSIDE ""

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
    
    # WORDS AFTER $
    seperated_by_comment = []
    for l in textbox.get("1.0", tk.END).split("\n"):
        if "$" in l:
            seperated_by_comment.append(l[l.index("$")::])
    for word in seperated_by_comment:
        highlight(word, "PURPLE")

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
    global filename, textbox
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

def save_file(event=None):
    global recent_files_menu, recents, recents_changed, filename, file

    if file:
        with open(filename, 'a') as f:
            f.truncate(0)
            f.write(textbox.get("1.0", tk.END))
    else:
        file = asksaveasfile(defaultextension=".flow", filetypes=[("Flow files", "*.flow")])
        if file is not None:
            filename = file.name
            app.title(filename.split("/")[-1])
            with open(filename, "w") as file_t:
                file_t.write(textbox.get("1.0", tk.END))
    # RECENTS MANAGEMENT
    recents_changed = False
    with open('fide/recents.txt', 'r') as recents_file:
        recents = recents_file.readlines()
        recents = [line.rstrip() for line in recents]
        if file not in recents:
            recents.insert(0, filename)
            if len(recents) > 4:
                recents.pop(4)
            recents_changed = True
    if recents_changed:
        with open('fide/recents.txt', 'w') as recents_file:
            recents_file.write("\n".join(recents))

def run_file(event=None):
    global terminal, flow_path, file, VARS
    save_file()
    if file:
        VARS = {}
        terminal.start_process(["python", os.path.normpath(flow_path), os.path.normpath(file), "FIDE"])

def exita(event=None):
    sys.exit()

def clear_console(event=None):
    global terminal
    terminal.text.configure(state="normal")
    terminal.text.delete('1.0', tk.END)
    terminal.text.configure(state="disabled")

def open_file(filename):
    global textbox, file, recent_files_menu, filename

    if not filename.endswith(".flow"):
        response = tk.messagebox.showwarning(title=f"⚠️ {filename} is not compatible",
                                         message=f"{filename} should have an extension .flow, its not compatible")
        return

    if not os.path.exists(filename):
        response = tk.messagebox.showwarning(title=f"⚠️ can't find {filename} directory ⚠️",
                                                message=f"{filename} does not exist")
        return

    # RECENTS MANAGEMENT
    recents_changed = False
    with open('fide/recents.txt', 'r') as recents_file:
        recents = recents_file.readlines()
        recents = [line.rstrip() for line in recents]
        if filename not in recents:
            recents.insert(0, filename)
            if len(recents) > 4:
                recents.pop(4)
            recents_changed = True
    if recents_changed:
        with open('fide/recents.txt', 'w') as recents_file:
            recents_file.write("\n".join(recents))

    if file is not None:
        with open(filename, 'r') as file_content:
            file_content = file_content.read()
            textbox.delete("1.0", tk.END)
            textbox.insert(tk.INSERT, file_content[:-1])
            update_text()
            terminal.text.delete("1.0", tk.END)
            app.title(filename.split("/")[-1])
        file = filename
    else:
        app.title("untitled.flow")
    
    # set recent files to menu
    if recents_changed:
        with open("fide/recents.txt","r") as recents:
            recent_files_menu.delete(0,4)
            for r in recents.readlines():
                r = r.rstrip()
                recent_files_menu.add_command(label=r.split("/")[-1], command=lambda fname=r: open_file(fname))


def open_file_from_dialog(event=None):
    global file
    # take filename from dialog box
    file = askopenfile(mode='r', filetypes=[('Flow Files', '*.flow')])
    if file is not None: 
        filename=file.name
        # open it
        open_file(filename)


############
### MAIN ###
############

print("\nrunning FIDE...")

#Setting file to NONE
file = None

# WIDGETS (Same as original code, except terminal replaced)
textbox = tk.Text(app, width=57, height=23, font=("Consolas 20"), undo=True, wrap="none")
textbox.place(rely=0, relx=0.04)
textbox.tag_config("GREEN", foreground="green")
textbox.tag_config("RED", foreground="red")
textbox.tag_config("ORANGE", foreground="orange")
textbox.tag_config("BLUE", foreground="lightblue")
textbox.tag_config("PURPLE", foreground="purple")
textbox.config(spacing1=10)

# VARIABLE TEXTBOX
variable_box = tk.Text(app, width=11, height=8, font=("Consolas 16"))
variable_box.place(rely=0.105, relx=0.7511)
variable_box.config(state="disabled")

variable_label = tk.Label(app, text="║VARS║\n╚====╝", font=("Consolas 20"), fg="lightblue")
variable_label.place(relx=0.76, rely=-0)

# FUNCTION TEXTBOX
function_box = tk.Text(app, width=11, height=8, font=("Consolas 16"))
function_box.place(rely=0.105, relx=0.887)
function_box.config(state="disabled")

function_label = tk.Label(app, text="║FUNS║\n╚====╝", font=("Consolas 20"), fg="lightblue")
function_label.place(relx=0.91, rely=0)

VARS_CONNECTION_KEY = "[SENDING_VARS_TO_FIDE]"
FUNS_CONNECTION_KEY = "[SENDING_FUNS_TO_FIDE]"
INPUT_CONNECTION_KEY = "[RUNNING_IN_FIDE]"

line_counter = tk.Text(app, width=3, height=23, font=("Consolas 20"), fg="lightblue", state="disabled")
line_counter.place(rely=-0, relx=0)
line_counter.config(spacing1=10)

# Replace the tkterminal with the new InteractiveConsole
terminal = InteractiveConsole(app)
terminal.place(relx=0.751, rely=0.57)

clear_console = tk.Button(app, text="CLEAR ×", fg="red", command = clear_console, font=("Consolas 7"))
clear_console.place(relx=0.97, rely=0.55,anchor=tk.CENTER)

console_label = tk.Label(app, text="║ CONSOLE ║\n╚=========╝", font=("Consolas 20"), fg="lightblue")
console_label.place(relx=0.81, rely=0.46799)

# MENU BAR (Unchanged)
menubar = tk.Menu()
file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(label="New", accelerator="Ctrl+n", command=new_file)
file_menu.add_command(label="Open", accelerator="Ctrl+o", command=open_file_from_dialog)

# RECENT FILES
recent_files_menu = tk.Menu(file_menu, tearoff=False)
file_menu.add_cascade(menu=recent_files_menu, label="Open Recents", accelerator="Ctrl+O")

# load recent files
with open("fide/recents.txt","r") as recents:
    for r in recents.readlines():
        r = r.rstrip()
        recent_files_menu.add_command(label=r.split("/")[-1], command=lambda fname=r: open_file(fname))

file_menu.add_command(label="Save", accelerator="Ctrl+s", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", accelerator="Ctrl+e", command=exit)
menubar.add_cascade(menu=file_menu, label="File")

run_menu = tk.Menu(menubar, tearoff=False)
run_menu.add_command(label="Run", accelerator="F5", command=run_file)
menubar.add_cascade(menu=run_menu, label="Run")

configuration_menu = tk.Menu(menubar, tearoff=False)
configuration_menu.add_command(label = "Intepreter",  accelerator="Ctrl + i", command = interpreter_configuration)
menubar.add_cascade(menu=configuration_menu, label="Configure")

app.config(menu=menubar)

# Bindings (Unchanged)
app.bind("<Control-n>", new_file)
app.bind("<Control-o>", open_file_from_dialog)
app.bind("<Control-s>", save_file)
app.bind("<Control-e>", exit)
app.bind("<F5>", run_file)

app.bind_all('<Key>', update_text)
app.bind_all('<Return>', update_text)

# THEME AND MAIN LOOP
sv_ttk.set_theme("dark")
app.mainloop()
