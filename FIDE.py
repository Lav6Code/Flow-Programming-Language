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
import time
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
        global FILENAME

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

        self.text.insert(tk.END, f"\n\nEXECUTING: {FILENAME.split('/')[-1]}\n{'═'*37}\n")
        self.text.see(tk.END)

        threading.Thread(target=self.read_output, daemon=True).start()

    def read_output(self):
        """Reads output from the subprocess."""

        for line in iter(self.process.stdout.readline, ""):
            if line.startswith(VARS_CONNECTION_KEY):
                # read VARS
                VARS = {}
                vars_ = line[len(VARS_CONNECTION_KEY):-1]
                vars_ = vars_.replace("True", "'TRUE'")
                vars_ = vars_.replace("False", "'False'")
                VARS = eval(vars_)
                #print(VARS)

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
DEVELOPER_MODE = False
WIDTH, HEIGHT = 1207, 700
app = tk.Tk()
app.geometry(str(WIDTH) + "x" + str(HEIGHT))
app.lift()
app.title("untitled.flow")
app.resizable(False, False)

# FLOW SETUP
GRERN_KEYWORDS = ['+', '*', "-", "/", "<", "<=", ">", ">=", "="]
RED_KEYWORDS = ['var', 'func', 'output', "input", "if", "for", "while", "fetch", "intersection", "union", "disjunction", "superset", "subset", "len", "call"]
ORANGE_KEYWORDS = ["1", "2", "3", "3", "4", "5", "6", "7", "8", "9", "0", '"', "num", "set", "txt", "bln"]
BLUE_KEYWORDS = [";", "(", ")"]
PINK_KEYWORDS = ["TRUE", "FALSE"]
PURPLE_KEYWORDS = ["$"] # COMMENT
COMMANDS = GRERN_KEYWORDS+ RED_KEYWORDS + BLUE_KEYWORDS + PINK_KEYWORDS + PURPLE_KEYWORDS + ORANGE_KEYWORDS
# FLOW path
FLOW_PATH = "./FLOW.py"

# Opened file
FILENAME = None


# FUNCTIONS (Unchanged from your original implementation)
def change_path_f():
    global FLOW_PATH, intpreter_configuration_window
    
    flow_file = askopenfile(title="Select Flow Intpereter", mode ='r', filetypes =[('Python', '*.py')])
    if flow_file is not None:
        FLOW_PATH = flow_file.name
    else:
        FLOW_PATH = None
    intpreter_configuration_window.destroy()

def developer_mode(event=None):
    global DEVELOPER_MODE, configuration_menu

    DEVELOPER_MODE = not(DEVELOPER_MODE)

    if DEVELOPER_MODE:
        configuration_menu.entryconfigure(1, label="Developer Mode ✓")
    else:
        configuration_menu.entryconfigure(1, label="Developer Mode ✗")

def interpreter_configuration(event=None):
    global intpreter_configuration_window
    intpreter_configuration_window = tk.Toplevel(app)
    intpreter_configuration_window.geometry("750x150")
    intpreter_configuration_window.title("Configure Intepreter")
    intpreter_configuration_window.after(10, intpreter_configuration_window.lift)
    
    current_intepreter_title = tk.Label(master=intpreter_configuration_window, text="╔{ CURRENT INTEPRETER }╗", fg="#3277a8", font = ("Calibri Bold", 16))
    current_intepreter_title.pack()
    
    current_path = tk.Label(master=intpreter_configuration_window, text="", font = "Consolas 12", bg = "#8f99a1", fg = "#000")
    if FLOW_PATH:
        current_path.config(text=FLOW_PATH)
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
        if variables[v] in "TRUE FALSE".split(" "):
            insert_text += f"{v}={variables[v]}\n"
        elif type(variables[v]) == int:
            insert_text += f"{v}={variables[v]}\n"
        elif type(variables[v]) == str:
            insert_text += f"{v}='{variables[v]}'\n" # ' for representing string(TXT)
        elif type(variables[v]) == list:
            insert_text += f"{v}={variables[v]}\n"

    variable_box.insert("1.0",insert_text)
    variable_box.config(state="disabled")

def update_functions_textbox(functions):
    global function_box
    function_box.config(state="normal")
    function_box.delete("1.0", tk.END)
    insert_text = ""
    
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

def update_line_counter(event=None):
    global line_counter, textbox

    n = textbox.get("1.0", tk.END).count("\n")
    text = ""
    for i in range(n):
        text += f"{i + 1}\n"
    text = text[:-1]
    
    line_counter.config(state="normal")
    line_counter.delete('1.0', tk.END)
    line_counter.insert('1.0', text)
    line_counter.yview_moveto(textbox.yview()[0])
    yview_real = line_counter.yview()[0]
    
    line_counter.config(state="disabled")

def update_text(a=None):
    global line_counter, textbox
    textbox.edit_modified(False)
    textbox.tag_remove("GREEN", 1.0, tk.END)
    textbox.tag_remove("RED", 1.0, tk.END)
    textbox.tag_remove("BLUE", 1.0, tk.END)
    textbox.tag_remove("ORANGE", 1.0, tk.END)
    textbox.tag_remove("PURPLE", 1.0, tk.END)
    textbox.tag_remove("PINK", 1.0, tk.END)

    for word in GRERN_KEYWORDS:
        highlight(word, "GREEN")
    for word in RED_KEYWORDS:
        highlight(word, "RED")
    for word in BLUE_KEYWORDS:
        highlight(word, "BLUE")
    for word in PINK_KEYWORDS:
        highlight(word, "PINK")

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

    check_autocompletion()
    update_line_counter()

def auto_finish(event=None):
    global textbox
    textbox.edit_modified(False)
    char_mapping = {"(": ")", '"': '"', "[": "]", "{": "}"}
    if event.char in char_mapping.keys():
        current_position = textbox.index(tk.INSERT)
        textbox.insert(current_position, char_mapping[event.char])
        textbox.mark_set(tk.INSERT, current_position)

def focus_text_widget():
    textbox.focus_force()

def new_file(event=None):
    global FILENAME, textbox
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
    FILENAME = None
    app.title("Untitled.flow")

def save_file(event=None):
    global recent_files_menu, recents, recents_changed, FILENAME

    if FILENAME:
        with open(FILENAME, 'a') as f:
            f.truncate(0)
            f.write(textbox.get("1.0", tk.END))
    else:
        file = asksaveasfile(defaultextension=".flow", filetypes=[("Flow files", "*.flow")])
        if file is not None:
            FILENAME = file.name
            app.title(FILENAME.split("/")[-1])
            with open(FILENAME, "w") as file_t:
                file_t.write(textbox.get("1.0", tk.END))

    # RECENTS MANAGEMENT
    recents_changed = False
    with open('fide/recents.txt', 'r') as recents_file:
        recents = recents_file.readlines()
        recents = [line.rstrip() for line in recents]
        if FILENAME not in recents:
            recents.insert(0, FILENAME)
            if len(recents) > 4:
                recents.pop(4)
            recents_changed = True
    if recents_changed:
        with open('fide/recents.txt', 'w') as recents_file:
            recents_file.write("\n".join(recents))
    # Update recents
    update_recents()

def update_recents():
    global recent_files_menu
    # load recent files
    with open("fide/recents.txt","r") as recents:
        recent_files_menu.delete(0,4)
        for r in recents.readlines():
            r = r.rstrip()
            recent_files_menu.add_command(label=r.split("/")[-1], command=lambda fname=r: open_file(fname))

def run_file(event=None):
    global terminal, FLOW_PATH, FILENAME, VARS
    save_file()
    if FILENAME:
        VARS = {}
        #CLEANING BOXS
        variable_box.config(state="normal")
        function_box.config(state="normal")
        variable_box.delete("1.0", tk.END)
        function_box.delete("1.0", tk.END)
        variable_box.config(state="disabled")
        function_box.config(state="disabled")

        # ACTUALLY RUNNING
        if not DEVELOPER_MODE:
            developer_mode_arg = ""
        else:
            developer_mode_arg = "DEVELOPER_MODE"
        terminal.start_process(["python", os.path.normpath(FLOW_PATH), os.path.normpath(FILENAME), "FIDE",developer_mode_arg])

def exita(event=None):
    sys.exit()

def clear_console(event=None):
    global terminal
    terminal.text.configure(state="normal")
    terminal.text.delete('1.0', tk.END)
    terminal.text.configure(state="disabled")

def open_file(filename):
    global textbox, FILENAME, recent_files_menu
    
    if not filename.endswith(".flow"):
        response = tk.messagebox.showwarning(title=f"⚠️ {filename} is not compatible",
                                         message=f"{filename} should have an extension .flow, its not compatible")
        return

    if not os.path.exists(filename):
        response = tk.messagebox.showwarning(title=f"⚠️ can't find {filename} directory ⚠️",
                                                message=f"{filename} does not exist")
        return

    FILENAME = filename

    # RECENTS MANAGEMENT
    recents_changed = False
    with open('fide/recents.txt', 'r') as recents_file:
        recents = recents_file.readlines()
        recents = [line.rstrip() for line in recents]
        if FILENAME not in recents:
            recents.insert(0, FILENAME)
            if len(recents) > 4:
                recents.pop(4)
            recents_changed = True
    if recents_changed:
        with open('fide/recents.txt', 'w') as recents_file:
            recents_file.write("\n".join(recents))

    # reading the file
    if FILENAME is not None:
        with open(FILENAME, 'r') as file_content:
            file_content = file_content.read()
            textbox.delete("1.0", tk.END)
            textbox.insert(tk.INSERT, file_content[:-1])
            update_text()
            terminal.text.delete("1.0", tk.END)
            app.title(FILENAME.split("/")[-1])
    else:
        app.title("untitled.flow")
    
    # set recent files to menu
    if recents_changed:
        update_recents()

def open_file_from_dialog(event=None):
    # take filename from dialog box
    file = askopenfile(mode='r', filetypes=[('Flow Files', '*.flow')])
    if file is not None: 
        filename = file.name
        # open it
        open_file(filename)

def insert_new_variable(event = None):
    global textbox

    new_variable_text = 'var("N", 0);\n'
    textbox.insert(textbox.index(tk.INSERT), new_variable_text)
    update_text()

def insert_new_function(event = None):
    global textbox

    new_function_text = '''func("FUN",(

));
call("FUN");\n'''
    textbox.insert(textbox.index(tk.INSERT), new_function_text)
    update_text()

def insert_new_while_loop(event = None):
    global textbox

    new_while_loop_text = '''
while( ,(

));\n'''
    textbox.insert(textbox.index(tk.INSERT), new_while_loop_text)
    update_text()

def insert_new_for_loop(event = None):
    global textbox

    new_for_loop_test = '''for( ,(

));\n'''
    textbox.insert(textbox.index(tk.INSERT), new_for_loop_test)
    update_text()

def insert_new_if_else(event = None):
    global textbox

    new_for_if_else = '''if(  ,(

),
(

));\n'''
    textbox.insert(textbox.index(tk.INSERT), new_for_if_else)
    update_text()

def show_autocomplete(x,y, commands):
    global autocomplete, textbox

    if autocomplete is not None:
        autocomplete.destroy()
        #print("autocomplete destroyed")
    
    if commands == []:
        return

    # Create a Listbox for autocomplete
    autocomplete = tk.Listbox(app, height=len(commands), bg="lightgrey", fg="black", selectbackground="blue")
    autocomplete.place(x=x, y=y)
    
    for command in commands:
        autocomplete_suggestions = autocomplete.get(0,tk.END)
        if command not in autocomplete_suggestions:
            autocomplete.insert(tk.END, command)
    autocomplete.select_set(0)
    #('new autocpomplete created and select 0')

def autocompletion(event=None):
    global autocomplete, textbox, app

    if app.focus_get() == textbox:
        ...
    else:
        return

    if autocomplete:
        app.update()
        index = textbox.index(tk.INSERT)
        line_number = str(index.split('.')[0])
        line_text = textbox.get(line_number+".0", index)[::-1]
        #print(autocomplete.curselection())
        word_to_complete = autocomplete.get(0, tk.END)[autocomplete.curselection()[0]]
        #print(word_to_complete)

    user_typed = ""
    for s in line_text:
        user_typed += s
        #print(user_typed)
        if word_to_complete.startswith(user_typed[::-1]):
            textbox.insert(index, word_to_complete[len(user_typed)::])
    
    autocomplete.destroy()
    app.update()
            

def check_autocompletion(event=None):
    global autocomplete, textbox, app

    textbox.edit_modified(False)

    if app.focus_get() == textbox:
        ...
    else:
        return

    index = textbox.index(tk.INSERT)
    line_number = str(index.split('.')[0])
    line_text = textbox.get(line_number+".0", index)[::-1]
    bbox = textbox.bbox(index)
    auto_complete_threshold = 2
    if bbox:
        # bbox returns (x, y, width, height); we take x, y for the position
        x, y = bbox[0], bbox[1]
        y += 30
        x += 55
        user_typed = ""
        possible_commands = []
        longest_command = len(max(COMMANDS, key = len))
        #print(longest_command)
        for s in line_text:
            user_typed += s
            for c in COMMANDS:
                if c.startswith(user_typed[::-1]) and len(user_typed) >= auto_complete_threshold and c != user_typed[::-1]:
                    possible_commands.append(c)

        if possible_commands:
            show_autocomplete(x,y,possible_commands)
        elif autocomplete:
            autocomplete.destroy()

def shuffle_complete_suggestions(event=None):

    global autocomplete, app

    if autocomplete:
        Noptions = len(autocomplete.get(0, tk.END))
        index_sel = autocomplete.curselection()[0]
        index_new = (index_sel + 1) % Noptions
        autocomplete.select_clear(0, tk.END)
        autocomplete.select_set(index_new)
        
        autocomplete.update()

############
### MAIN ###
############

print("\nrunning FIDE...")

# check if recents exist
if not os.path.exists("fide/recents.txt"):
    f = open("fide/recents.txt", "x")
    f.close()

# WIDGETS (Same as original code, except terminal replaced)

textbox = tk.Text(app, width=57, height=18, font=("Consolas 20"), undo=True, wrap="none")
textbox.place(rely=0, relx=0.04)
textbox.tag_config("GREEN", foreground="green")
textbox.tag_config("RED", foreground="#d1644a")
textbox.tag_config("ORANGE", foreground="#FFC300")
textbox.tag_config("BLUE", foreground="#57c1d9")
textbox.tag_config("PURPLE", foreground="#634a7f")
textbox.tag_config("PINK", foreground="#e57bff")
textbox.config(spacing1=5)

line_counter = tk.Text(app, width=3, height=18, font=("Consolas 20"), fg="lightblue", state="disabled", wrap="none")
line_counter.place(rely=0, relx=0)
line_counter.config(spacing1=5)

# VARIABLE TEXTBOX
variable_box = tk.Text(app, width=11, height=8, font=("Consolas 16"))
variable_box.place(rely=0.105, relx=0.7511)
variable_box.config(state="disabled")

variable_label = tk.Label(app, text="║VARS║\n╚====╝", font=("Consolas 20"), fg="lightblue")
variable_label.place(relx=0.77, rely=-0)

# FUNCTION TEXTBOX
function_box = tk.Text(app, width=11, height=8, font=("Consolas 16"))
function_box.place(rely=0.105, relx=0.887)
function_box.config(state="disabled")

function_label = tk.Label(app, text="║FUNS║\n╚====╝", font=("Consolas 20"), fg="lightblue")
function_label.place(relx=0.905, rely=0)

VARS_CONNECTION_KEY = "[SENDING_VARS_TO_FIDE]"
FUNS_CONNECTION_KEY = "[SENDING_FUNS_TO_FIDE]"
INPUT_CONNECTION_KEY = "[RUNNING_IN_FIDE]"

# Replace the tkterminal with the new InteractiveConsole
terminal = InteractiveConsole(app)
terminal.place(relx=0.751, rely=0.53)

clear_console = tk.Button(app, text="CLEAR ×", fg="red", command = clear_console, font=("Consolas 7"))
clear_console.place(relx=0.97, rely=0.50,anchor=tk.CENTER)

console_label = tk.Label(app, text="║ CONSOLE ║\n╚=========╝", font=("Consolas 20"), fg="lightblue")
console_label.place(relx=0.81, rely=0.42)

# MENU BAR (Unchanged)
menubar = tk.Menu()
file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(label="New", accelerator="Ctrl+n", command=new_file)
file_menu.add_command(label="Open", accelerator="Ctrl+o", command=open_file_from_dialog)
# RECENT FILES
recent_files_menu = tk.Menu(file_menu, tearoff=False)
file_menu.add_cascade(menu=recent_files_menu, label="Open Recents", accelerator="Ctrl+O")
file_menu.add_command(label="Save", accelerator="Ctrl+s", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", accelerator="Ctrl+e", command=exit)
menubar.add_cascade(menu=file_menu, label="File")

insert_menu = tk.Menu(menubar, tearoff=False)
insert_menu.add_command(label = "New Variable",  accelerator="Ctrl+Shift+v", command = insert_new_variable)
insert_menu.add_command(label = "New Function",  accelerator="Ctrl+Shift+f", command = insert_new_function)
insert_menu.add_command(label = "New For Loop",  accelerator="Ctrl+Alt+o", command = insert_new_for_loop)
insert_menu.add_command(label = "New While Loop",  accelerator="Ctrl+Shift+w", command = insert_new_while_loop)
insert_menu.add_command(label = "New If Else",  accelerator="Ctrl+Shift+I", command = insert_new_while_loop)
menubar.add_cascade(menu=insert_menu, label="Insert")

run_menu = tk.Menu(menubar, tearoff=False)
run_menu.add_command(label="Run", accelerator="F5", command=run_file)
menubar.add_cascade(menu=run_menu, label="Run")

configuration_menu = tk.Menu(menubar, tearoff=False)
configuration_menu.add_command(label = "Intepreter",  accelerator="Ctrl+i", command = interpreter_configuration)
configuration_menu.add_command(label = "Developer Mode ✗",  accelerator="Ctrl+d", command = developer_mode)
menubar.add_cascade(menu=configuration_menu, label="Configure")

app.config(menu=menubar)

# assigning autocomplete to None, so it does not crash when trying to check if autocomplete exists
autocomplete = None

# Recents

update_recents()

# Line counter

update_line_counter()

# Bindings (Unchanged)
app.bind("<Control-n>", new_file)
app.bind("<Control-o>", open_file_from_dialog)
app.bind("<Control-s>", save_file)
app.bind("<Control-e>", exit)
app.bind("<F5>", run_file)
app.bind("<Control-i>", interpreter_configuration)
app.bind("<Control-d>", developer_mode)
app.bind("<Control-V>", insert_new_variable)
app.bind("<Control-F>", insert_new_function)
app.bind("<Control-O>", insert_new_for_loop)
app.bind("<Control-W>", insert_new_while_loop)
app.bind("<Control-I>", insert_new_if_else)

app.bind("<Control-space>", autocompletion)
app.bind("<Control-q>", shuffle_complete_suggestions)
textbox.bind_all('<<Modified>>', check_autocompletion)
textbox.bind_all('<<Modified>>', auto_finish)
textbox.bind_all('<<Modified>>', update_text)
textbox.bind_all('<MouseWheel>', update_line_counter)
textbox.bind_all("<Key>", update_line_counter)

# THEME AND MAIN LOOP
sv_ttk.set_theme("dark")
app.mainloop()
