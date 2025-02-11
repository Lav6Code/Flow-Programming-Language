# ------- IMPORTS -------- #

import tkinter as tk
from tkinter.filedialog import *
import sys
import os
import subprocess
import threading
import queue
from pathlib import Path
import ctypes

# ------- INTERACTIVE CONSOLE -------- #
class InteractiveConsole(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, font=("Consolas", 11), height=16, width=37, background=BACKGROUND_COLOR, foreground="#cdd6f4", insertbackground=FOREGROUND_COLOR)
        self.text.pack(expand=True, fill=tk.BOTH)
        self.text.bind("<Return>", self.on_enter)
        self.text.configure(state="disabled")

        self.process = None
        self.input_queue = queue.Queue()

    def start_process(self, command):
        global FILENAME
        restrict_input()
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
                vars_ = vars_.replace("False", "'FALSE'")
                VARS = eval(vars_)
                

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

    def cancel_process(self):
            """Terminates the running subprocess, if any."""
            if self.process is not None and self.process.poll() is None:
                self.process.terminate()  # Attempt to terminate the process
                self.process.wait()  # Ensure the process has stopped
                self.text.configure(state="normal")
                self.text.insert(tk.END, "Process terminated by user.\n")
                self.text.configure(state="disabled")
                self.text.see(tk.END)
                self.process = None  # Reset the process reference
            else:
                self.text.configure(state="normal")
                self.text.insert(tk.END, "No running process to terminate.\n")
                self.text.configure(state="disabled")
                self.text.see(tk.END)

# ------- SETUP -------- #
DEVELOPER_MODE = False
WIDTH, HEIGHT = 1207, 700
BACKGROUND_COLOR = "#1e1e2e"
FOREGROUND_COLOR = "#cdd6f4"

APP = tk.Tk()
APP.configure(background=BACKGROUND_COLOR)
APP.geometry(str(WIDTH) + "x" + str(HEIGHT))
APP.lift()
APP.title("untitled.flow")
APP.resizable(False, False)
APP.iconbitmap(".\\assets\\fide_icon.ico")

# FLOW SETUP
ORANGE_KEYWORDS = ["1", "2", "3", "3", "4", "5", "6", "7", "8", "9", "0"]
RED_KEYWORDS = ['var', 'func', 'output', "input", "if", "for", "while", "fetch", "intersection", "union", "seq","disjunction", "superset", "subset", "len", "call", "add", "num", "set", "txt", "bln", "get", "object", "attr", "loop",'+', '*', "-", "/", "<", "<=", ">", ">=", "=", "and", "xor", "or", "not"]
GREEN_KEYWORDS = ['"']
LIGHT_BLUE_KEYWORDS = [";", "(", ")"]
PINK_KEYWORDS = ["TRUE", "FALSE"]
BLUE_KEYWORDS = ["Circle", "Triangle", "Polyline", "Line", "draw"]
PURPLE_KEYWORDS = ["$"] # COMMENT
COMMANDS = GREEN_KEYWORDS+ RED_KEYWORDS + BLUE_KEYWORDS + PINK_KEYWORDS + PURPLE_KEYWORDS + ORANGE_KEYWORDS + BLUE_KEYWORDS
COMMANDS_DESCRIPTION = {"+":"+(arg1 [num|txt], arg2 [num|txt]) -> sum or concatination of arg1 and arg2",
                        "-":"-(arg1 [num], arg2 [num]) -> substraction of arg1 and arg2",
                        "*":"*(arg1 [num], arg2 [num]) -> procuct of arg1 and arg2",
                        "/":"/(arg1 [num], arg2 [num]) -> values that are going to be divided",
                        "<":"<(arg1 [num], arg2 [num]) -> TRUE if arg1 is less than arg2",
                        ">":">(arg1 [num], arg2 [num]) -> TRUE if arg1 is greater than arg2",
                        "<=":"<=(arg1 [num], arg2 [num]) -> TRUE if arg1 is less or equal than arg2",
                        ">=":">=(arg1 [num], arg2 [num]) -> TRUE if arg1 is greater or equal than arg2",
                        "=":"=(arg1 [num], arg2 [num]) -> TRUE if arg1 is equal to arg2",
                        "and":"and(bln1 [bln], bln2 [bln]) -> TRUE if arg1 and arg2 are TRUE",
                        "or":"or(bln1 [bln], bln2 [bln]) -> TRUE if at least one arg1 and arg2 are TRUE",
                        "xor":"xor(bln1 [bln], bln2 [bln]) -> TRUE if only one of two blns is TRUE",
                        "not":"not(bln1 [bln]) -> opposite boolean value of bln1, TRUE -> FALSE, FALSE -> TRUE",
                        "var":"var(varname [txt], val [txt|num|bln|set]) -> defines or updates a variable with the name varname with the value val",
                        "func":"func(fname [txt], codeblock [blk]) -> defines a function with the name fname and body codeblock",
                        "output":"output(str [txt]) -> outputs the str into console",
                        "input":'input(datatype ["num"|"txt"|"bln"]) -> takes text from keyboard and converts it into data of type datatype',
                        "if":"if(bln, blk, blk*) -> if the bln is TRUE the blk will run, ELSE the blk* will run, blk* is optional",
                        "loop":"loop(n [num], codeblock [blk]) -> runs the codeblock n times",
                        "for":"for(index [txt], array [set], codeblock [blk]) -> iterates through array, assigning each element to index and executing codeblock",
                        "seq":"seq([start] [num], stop [num], [step] [num]) – Returns a 'set' from 'start' to stop with step 'step'. Defaults: start=0, step=1",
                        "while":"while(condition [bln], codeblock [blk]) -> repeatedly run codeblock, while the condition is TRUE",
                        "fetch":"fetch(set, num) -> the num-th element of the set",
                        "intersection":"intersection(set1 [set], set2 [set]) -> the intersection of the two sets (set of elements that are present in both given sets)",
                        "union":"union(set1 [set], set2 [set]) -> union of two sets (set of unique elements of both sets combined)",
                        "disjunction":"disjunction(set1 [set], set2 [set]) -> the disjunction of the two sets (set of elements that are uniqe to each given set)",
                        "superset":"superset(set1 [set], set2 [set]) -> TRUE if all elements of set2 are in set1, otherwise FALSE",
                        "subset":"subset(set1 [set], set2 [set]) -> TRUE if all elements of set1 are in set2, otherwise FALSE",
                        "len":"len(arg [set]) -> length of set arg",
                        "add":"add(arg [set], app [txt|num|bln|set]) -> set produced by appending app to the set arg",
                        "call":"call(fname [txt]) -> calls (runs) the function by the name of fname",
                        'set':'set(el1 [txt|num|bln|set], el2 [txt|num|bln|set], ...) -> set with elements el1, el2..., enter only "_" for empty set',
                        "num":"num(arg [txt]) -> converts arg into type num, if possible",
                        "txt":"txt(arg [num]) -> converts arg into txt, if possible",
                        "bln":"bln(arg [txt|num]) -> converts arg into bln, if possible",
                        "sum":"sum(set [set] or el1 [num], el2[num]...) -> sum of all elements in a set, or sum of all arguments (el1, el1...)",
                        "max":"max(set [set] or el1 [num], el2[num]...) -> highest value of all elements in a set, or highest value of all arguments (el1, el1...)",
                        "min":"min(set [set] or el1 [num], el2[num]...) -> lowest value of all elements in a set, or lowest value of all arguments (el1, el1...)",
                        "object":"object(name [txt]) -> creates an emtpy object with no attributes",
                        "attr":"attr(object [txt], attribute [txt], value [txt|num|bln|set]) -> creates an attribute and adds it into object",
                        "get":"get(object [txt], attribute [txt]) -> value of attribute inside the object",
                        "Line":"Line(point [set], point [set]) -> object with name, points, length attributes",
                        "Polyine":"Polyine(point [set], point [set]...) -> object with name, points, length attributes",
                        "Triangle":"Triangle(point [set], point [set], point [set]) -> object with name, points, perimeter, area, sides attributes",
                        "Circle":"Circle(center [set], radius [num]) -> object with name, center, perimeter, area, diameter attributes that represent a circle",
                        "InCircle":"Circle(triangle [obj]) -> object with name, center, perimeter, area, diameter attributes represent a circle inside a triangle",
                        "draw":"draw(shape [obj], shape [obj]...) -> opens new window and visually shows the shapes",
                        }

HELP_KEYWORD1 = list(COMMANDS_DESCRIPTION.keys())
HELP_KEYWORD2 = ["->"]
HELP_KEYWORD3 = ["txt","set","num","bln","txt1","set1","num1","bln1","txt2","set2","num2","bln2","blk*","BLK","BLN","SET","sets", "obj", "object"]
HELP_KEYWORD4 = ["┃"]
# FLOW path
FLOW_PATH = "./FLOW.py"

# Opened file
FILENAME = None

# ------- FUNCTIONS -------- #
def change_path_f():
    global FLOW_PATH, intpreter_configuration_window
    
    flow_file = askopenfile(title="Select Flow Intpereter", mode ='r', filetypes =[('Python', '*.py')])
    if flow_file is not None:
        FLOW_PATH = flow_file.name
    else:
        FLOW_PATH = None
    intpreter_configuration_window.destroy()

def developer_mode(event=None):
    global DEVELOPER_MODE, GUI_CONFIGURATION_MENU

    DEVELOPER_MODE = not(DEVELOPER_MODE)

    if DEVELOPER_MODE:
        GUI_CONFIGURATION_MENU.entryconfigure(1, label="Developer Mode ✓")
    else:
        GUI_CONFIGURATION_MENU.entryconfigure(1, label="Developer Mode ✗")

def interpreter_configuration(event=None):
    global intpreter_configuration_window
    intpreter_configuration_window = tk.Toplevel(APP)
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
    global GUI_VARIABLE_BOX
    GUI_VARIABLE_BOX.config(state="normal")
    GUI_VARIABLE_BOX.delete("1.0", tk.END)
    insert_text = ""
    name = "name"
    for v in variables:
        if variables[v] in "TRUE FALSE".split(" "):
            insert_text += f"{v}={variables[v].upper()}\n"
        elif type(variables[v]) == dict:
            insert_text += f"{v}={variables[v][name]}\n"
        elif type(variables[v]) == int:
            insert_text += f"{v}={variables[v]}\n"
        elif type(variables[v]) == str:
            insert_text += f"{v}='{variables[v]}'\n" # ' for representing string(TXT)
        elif type(variables[v]) == list:
            insert_text += f"{v}={variables[v]}\n"

    GUI_VARIABLE_BOX.insert("1.0",insert_text)
    GUI_VARIABLE_BOX.config(state="disabled")

def update_functions_textbox(functions):
    global GUI_FUNCTION_BOX
    GUI_FUNCTION_BOX.config(state="normal")
    GUI_FUNCTION_BOX.delete("1.0", tk.END)
    insert_text = ""
    
    for v in functions:
        insert_text += (v + "\n")

    GUI_FUNCTION_BOX.insert("1.0",insert_text)
    GUI_FUNCTION_BOX.config(state="disabled")

def highlight(keyword, tag_name, widget):
    start = "1.0"
    while True:
        pos = widget.search(keyword, start, stopindex=tk.END)
        end = f"{pos}+{len(keyword)}c"
        start = end
        if not pos:
            break
        if keyword == widget.get(pos, end):
            widget.tag_add(tag_name, pos, end)
            if tag_name == "PINK":
                widget.tag_add("BOLD", pos, end)
            if tag_name == "GREEN":
                widget.tag_add("ITALIC", pos, end)

def update_line_counter(event=None):
    global GUI_LINE_COUNTER, GUI_TEXTBOX

    n = GUI_TEXTBOX.get("1.0", tk.END).count("\n")
    text = ""
    for i in range(n):
        text += f"{i + 1}\n"
    text = text[:-1]
    
    GUI_LINE_COUNTER.config(state="normal")
    GUI_LINE_COUNTER.delete('1.0', tk.END)
    GUI_LINE_COUNTER.insert('1.0', text)
    GUI_LINE_COUNTER.yview_moveto(GUI_TEXTBOX.yview()[0])
    yview_real = GUI_LINE_COUNTER.yview()[0]
    
    GUI_LINE_COUNTER.config(state="disabled")

def update_text(a=None):
    global GUI_LINE_COUNTER, GUI_TEXTBOX, GUI_COMMAND_HELP
    
    # settings modified attribute to False so it can be changed again
    GUI_TEXTBOX.edit_modified(False)

    # removing all tags from the text box
    GUI_TEXTBOX.tag_remove("GREEN", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("PINK", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("BLUE", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("ORANGE", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("PINK", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("LIGHT_BLUE", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("PINK", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("BOLD", 1.0, tk.END)
    GUI_TEXTBOX.tag_remove("ITALIC", 1.0, tk.END)

    for word in GREEN_KEYWORDS:
        highlight(word, "GREEN", GUI_TEXTBOX)
    for word in RED_KEYWORDS:
        highlight(word, "PINK", GUI_TEXTBOX)
    for word in BLUE_KEYWORDS:
        highlight(word, "BLUE", GUI_TEXTBOX)
    for word in PINK_KEYWORDS:
        highlight(word, "PINK", GUI_TEXTBOX)
    for word in ORANGE_KEYWORDS:
        highlight(word, "ORANGE", GUI_TEXTBOX)
    for word in LIGHT_BLUE_KEYWORDS:
        highlight(word, "LIGHT_BLUE", GUI_TEXTBOX) 


    # WORDS INSIDE ""

    bucket = ""
    inside_n = []
    n_counter = 0
    for l in GUI_TEXTBOX.get("1.0", tk.END):
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
        highlight(word, "GREEN", GUI_TEXTBOX)
    
    # WORDS AFTER $
    seperated_by_comment = []
    for l in GUI_TEXTBOX.get("1.0", tk.END).split("\n"):
        if "$" in l:
            seperated_by_comment.append(l[l.index("$")::])
    for word in seperated_by_comment:
        highlight(word, "PURPLE", GUI_TEXTBOX)

    # Clear hint
    GUI_COMMAND_HELP.config(state="normal")
    GUI_COMMAND_HELP.delete("1.0", tk.END)
    GUI_COMMAND_HELP.config(state="disabled")

    check_autocompletion()
    update_line_counter()

def auto_finish(event):
    global GUI_TEXTBOX
    GUI_TEXTBOX.edit_modified(False)
    
    if event.keysym == "A":  # For the Enter key, you can do something special
        print("You pressed Enter!")
    elif event.keysym == "BackSpace":
        print("You pressed Backspace!")
    
    char_mapping = {"(": ")", '"': '"', "[": "]", "{": "}"}
    
    if event.char in char_mapping.keys():
        current_position = GUI_TEXTBOX.index(tk.INSERT)
        GUI_TEXTBOX.insert(current_position, char_mapping[event.char])
        GUI_TEXTBOX.mark_set(tk.INSERT, current_position)

def focus_text_widget():
    GUI_TEXTBOX.focus_force()

def new_file(event=None):
    global FILENAME, GUI_TEXTBOX
    response = tk.messagebox.askquestion(title="⚠️ File will not be saved! ⚠️",
                                             message="Save file before opening another file?", type="yesnocancel")
    if response == "yes":
        save_file()
        GUI_TEXTBOX.delete("1.0", tk.END)
        APP.update()
    elif response == "cancel":
        ...
    else:
        GUI_TEXTBOX.delete("1.0", tk.END)
        APP.update()
    FILENAME = None
    APP.title("Untitled.flow")

def save_file(event=None):
    global GUI_RECENT_FILES_MENU, recents, recents_changed, FILENAME

    if FILENAME:
        with open(FILENAME, 'a') as f:
            f.truncate(0)
            f.write(GUI_TEXTBOX.get("1.0", tk.END))
    else:
        file = asksaveasfile(defaultextension=".flow", filetypes=[("Flow files", "*.flow")])
        if file is not None:
            FILENAME = file.name
            APP.title(FILENAME.split("/")[-1])
            with open(FILENAME, "w") as file_t:
                file_t.write(GUI_TEXTBOX.get("1.0", tk.END))

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
        try:
            with open('fide/recents.txt', 'w') as recents_file:
                recents_file.write("\n".join(recents))
        except:
            ...
    # Update recents
    update_recents()

def update_recents():
    global GUI_RECENT_FILES_MENU
    # load recent files
    with open("./recents.txt","r") as recents:
        GUI_RECENT_FILES_MENU.delete(0,4)
        for r in recents.readlines():
            r = r.rstrip()
            GUI_RECENT_FILES_MENU.add_command(label=r.split("/")[-1], command=lambda fname=r: open_file(fname))

def run_file(event=None):
    global GUI_TERMINAL, FLOW_PATH, FILENAME, VARS
    save_file()
    if FILENAME:
        VARS = {}
        #CLEANING BOXS
        GUI_VARIABLE_BOX.config(state="normal")
        GUI_FUNCTION_BOX.config(state="normal")
        GUI_VARIABLE_BOX.delete("1.0", tk.END)
        GUI_FUNCTION_BOX.delete("1.0", tk.END)
        GUI_VARIABLE_BOX.config(state="disabled")
        GUI_FUNCTION_BOX.config(state="disabled")

        # ACTUALLY RUNNING
        if not DEVELOPER_MODE:
            developer_mode_arg = ""
        else:
            developer_mode_arg = "DEVELOPER_MODE"
        GUI_TERMINAL.start_process(["python", os.path.normpath(FLOW_PATH), os.path.normpath(FILENAME), "FIDE", developer_mode_arg])

def exita(event=None):
    sys.exit()

def clear_console(event=None):
    global GUI_TERMINAL
    GUI_TERMINAL.text.configure(state="normal")
    GUI_TERMINAL.text.delete('1.0', tk.END)
    GUI_TERMINAL.text.configure(state="disabled")
    GUI_TERMINAL.cancel_process()

def open_file(filename):
    global GUI_TEXTBOX, FILENAME, GUI_RECENT_FILES_MENU
    
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
            GUI_TEXTBOX.delete("1.0", tk.END)
            GUI_TEXTBOX.insert(tk.INSERT, file_content[:-1])
            update_text()
            GUI_TERMINAL.text.delete("1.0", tk.END)
            APP.title(FILENAME.split("/")[-1])
    else:
        APP.title("untitled.flow")
    
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
    global GUI_TEXTBOX

    new_variable_text = 'var("N", 0);\n'
    GUI_TEXTBOX.insert(GUI_TEXTBOX.index(tk.INSERT), new_variable_text)
    update_text()

def insert_new_function(event = None):
    global GUI_TEXTBOX

    new_function_text = '''func("FUN",(

));
call("FUN");\n'''
    GUI_TEXTBOX.insert(GUI_TEXTBOX.index(tk.INSERT), new_function_text)
    update_text()

def insert_new_while_loop(event = None):
    global GUI_TEXTBOX

    new_while_loop_text = '''
while( ,(

));\n'''
    GUI_TEXTBOX.insert(GUI_TEXTBOX.index(tk.INSERT), new_while_loop_text)
    update_text()

def insert_new_for_loop(event = None):
    global GUI_TEXTBOX

    new_for_loop_test = '''for("i", ,(

));\n'''
    GUI_TEXTBOX.insert(GUI_TEXTBOX.index(tk.INSERT), new_for_loop_test)
    update_text()

def insert_new_if_else(event = None):
    global GUI_TEXTBOX

    new_for_if_else = '''if(  ,(

),
(

));\n'''
    GUI_TEXTBOX.insert(GUI_TEXTBOX.index(tk.INSERT), new_for_if_else)
    update_text()

def command_help(c):
    global GUI_COMMAND_HELP

    string = COMMANDS_DESCRIPTION[c]
    length_of_help = 84
    words = string.split(" ")
    result = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > length_of_help:
            result.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " " + word
            else:
                current_line = word

    if current_line:
        result.append(current_line)
    
    string = "\n".join(result)

    GUI_COMMAND_HELP.config(state="normal")
    GUI_COMMAND_HELP.insert("1.0", string)
    # highlight
    GUI_COMMAND_HELP.tag_remove("help1", 1.0, tk.END)
    GUI_COMMAND_HELP.tag_remove("help2", 1.0, tk.END)
    GUI_COMMAND_HELP.tag_remove("help3", 1.0, tk.END)
    GUI_COMMAND_HELP.tag_remove("help4", 1.0, tk.END)
    GUI_COMMAND_HELP.tag_remove("help5", 1.0, tk.END)


    for word in HELP_KEYWORD1:
        highlight(word, "help1", GUI_COMMAND_HELP)
    for word in HELP_KEYWORD2:
        highlight(word, "help2", GUI_COMMAND_HELP)
    for word in HELP_KEYWORD3:
        highlight(word, "help3", GUI_COMMAND_HELP)
    for word in HELP_KEYWORD4:
        highlight(word, "help4", GUI_COMMAND_HELP)

    GUI_COMMAND_HELP.config(state="disabled")

def show_autocomplete(x,y, commands):
    global GUI_AUTOCOMPLETE, GUI_TEXTBOX

    if GUI_AUTOCOMPLETE is not None:
        GUI_AUTOCOMPLETE.destroy()
    
    if commands == []:
        return

    # Create a Listbox for GUI_AUTOCOMPLETE
    GUI_AUTOCOMPLETE = tk.Listbox(APP, height=len(commands), bg="#201c1c", fg="lightgrey", selectbackground="#6399f8", selectforeground="black")
    GUI_AUTOCOMPLETE.place(x=x, y=y)
    for command in commands:
        autocomplete_suggestions = GUI_AUTOCOMPLETE.get(0,tk.END)
        if command not in autocomplete_suggestions:
            GUI_AUTOCOMPLETE.insert(tk.END, command)
    GUI_AUTOCOMPLETE.select_set(0)
    #('new autocpomplete created and select 0')

def autocompletion(event=None):
    global GUI_AUTOCOMPLETE, GUI_TEXTBOX, APP

    if APP.focus_get() == GUI_TEXTBOX:
        ...
    else:
        return

    if GUI_AUTOCOMPLETE:
        APP.update()
        index = GUI_TEXTBOX.index(tk.INSERT)
        line_number = str(index.split('.')[0])
        line_text = GUI_TEXTBOX.get(line_number+".0", index)[::-1]
        word_to_complete = GUI_AUTOCOMPLETE.get(0, tk.END)[GUI_AUTOCOMPLETE.curselection()[0]]

    user_typed = ""
    for s in line_text:
        user_typed += s
        if word_to_complete.startswith(user_typed[::-1]):
            GUI_TEXTBOX.insert(index, word_to_complete[len(user_typed)::])
            command_help(word_to_complete)
    
    GUI_AUTOCOMPLETE.destroy()
    APP.update()
            
def check_autocompletion(event=None):
    global GUI_AUTOCOMPLETE, GUI_TEXTBOX, APP

    # settings modified attribute to False so it can be changed again
    GUI_TEXTBOX.edit_modified(False)

    if APP.focus_get() == GUI_TEXTBOX:
        ...
    else:
        return

    index = GUI_TEXTBOX.index(tk.INSERT)
    line_number = str(index.split('.')[0])
    line_text = GUI_TEXTBOX.get(line_number+".0", index)[::-1]
    bbox = GUI_TEXTBOX.bbox(index)
    auto_complete_threshold = 2
    if bbox:
        # bbox returns (x, y, width, height); we take x, y for the position
        x, y = bbox[0], bbox[1]
        y += 30
        x += 55
        user_typed = ""
        possible_commands = []
        longest_command = ""
        for s in line_text:
            user_typed += s
            for c in COMMANDS_DESCRIPTION.keys():
                if c.startswith(user_typed[::-1]) and len(user_typed) >= auto_complete_threshold and c != user_typed[::-1]:
                    possible_commands.append(c)
                if c == user_typed[::-1] or user_typed[::-1][:-1] == c :
                    if len(longest_command) < len(c):
                        longest_command = c

        if longest_command != "":
            command_help(longest_command)
        if possible_commands:
            show_autocomplete(x,y,possible_commands)
        elif GUI_AUTOCOMPLETE:
            GUI_AUTOCOMPLETE.destroy()

def shuffle_complete_suggestions(event=None):
    global GUI_AUTOCOMPLETE, APP

    if GUI_AUTOCOMPLETE:
        Noptions = len(GUI_AUTOCOMPLETE.get(0, tk.END))
        index_sel = GUI_AUTOCOMPLETE.curselection()[0]
        index_new = (index_sel + 1) % Noptions
        GUI_AUTOCOMPLETE.select_clear(0, tk.END)
        GUI_AUTOCOMPLETE.select_set(index_new)
        
        GUI_AUTOCOMPLETE.update()

def update_menu():
    global GUI_TOOL_MENU, SEARCHING, SELECTION

    GUI_TOOL_MENU.delete(0,"end")
    if SEARCHING:
        GUI_TOOL_MENU.add_command(label="Quit Search", command=quit_search)
    else:
        GUI_TOOL_MENU.add_command(label="Search", command=search)
    GUI_TOOL_MENU.add_command(label="Replace", command=open_replace_window) 
    # other commands ...

def show_menu(event):
    global SELECTION

    SELECTION = None
    try:
        SELECTION = GUI_TEXTBOX.get(tk.SEL_FIRST, tk.SEL_LAST)
    except:
        ...
    GUI_TOOL_MENU.tk_popup(event.x_root, event.y_root)

def search():
    global SELECTION, GUI_TEXTBOX, GUI_TOOL_MENU, SEARCHING
    if SELECTION:
        GUI_TEXTBOX.tag_remove("HIGHLIGHT", "1.0", tk.END)
        highlight(SELECTION, "HIGHLIGHT", GUI_TEXTBOX)
        SEARCHING = not(SEARCHING)
        GUI_TEXTBOX.update()
        update_menu()

def _():

    GUI_REPLACE_WINDOW.after(1, callback)
    return True

def callback():
    global SELECTION

    SELECTION = GUI_FIND_WORD.get()
    search()
    return True

def open_replace_window(event=None):
    global GUI_REPLACE_BUTTON, GUI_REPLACE_WORD, GUI_FIND_WORD, GUI_REPLACE_WINDOW

    GUI_REPLACE_WINDOW = tk.Toplevel(APP)
    GUI_REPLACE_WINDOW.geometry("300x200")
    GUI_REPLACE_WINDOW.title("Replace")
    GUI_REPLACE_WINDOW.iconbitmap(".\\assets\\fide_icon.ico")

    GUI_FIND_WORD_LABEL = tk.Label(GUI_REPLACE_WINDOW, text="Word that will be replaced", font="Consolas 10")
    GUI_FIND_WORD_LABEL.place(rely=0.15, relx=0.7, anchor=tk.E)

    sv = tk.StringVar()
    GUI_FIND_WORD = tk.Entry(GUI_REPLACE_WINDOW, textvariable=sv, validate="key", validatecommand=_, font="Consolas 17")
    GUI_FIND_WORD.place(relx = 0.5, rely = 0.3, anchor=tk.CENTER)

    GUI_REPLACE_WORD_LABEL = tk.Label(GUI_REPLACE_WINDOW, text="Replacement", font="Consolas 10")
    GUI_REPLACE_WORD_LABEL.place(rely=0.55, relx=0.345, anchor=tk.E)


    GUI_REPLACE_WORD = tk.Entry(GUI_REPLACE_WINDOW, font="Consolas 17")
    GUI_REPLACE_WORD.place(relx = 0.5, rely = 0.7, anchor=tk.CENTER)

    GUI_REPLACE_BUTTON = tk.Button(GUI_REPLACE_WINDOW, text="Replace", command=replace)
    GUI_REPLACE_BUTTON.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    # Setting the normal value for tk.Entry

    if SELECTION:
        GUI_FIND_WORD.insert(0, SELECTION)

def replace():
    global GUI_TEXTBOX, GUI_REPLACE_WORD, GUI_FIND_WORD, GUI_REPLACE_WINDOW

    textboxcontent = GUI_TEXTBOX.get("1.0", tk.END)
    textboxcontent = textboxcontent.replace(GUI_FIND_WORD.get(), GUI_REPLACE_WORD.get())
    GUI_TEXTBOX.delete("1.0", tk.END)
    GUI_TEXTBOX.insert("1.0", textboxcontent[:-1]) # \n situation
    GUI_REPLACE_WINDOW.destroy()
    quit_search()

def quit_search():

    global GUI_TOOL_MENU, SEARCHING, GUI_TEXTBOX

    GUI_TEXTBOX.tag_remove("HIGHLIGHT","1.0", tk.END)
    SEARCHING = False
    update_menu()

def delete_autocomplete(event=None):

    global GUI_AUTOCOMPLETE

    if GUI_AUTOCOMPLETE:
        GUI_AUTOCOMPLETE.destroy()

def restrict_input(event=None):
    """ Allows focus but forces cursor to stay on the last line when clicked """
    GUI_TERMINAL.text.after(1, move_cursor_to_last_line)  # Move cursor after event executes

def move_cursor_to_last_line():
    """ Moves cursor to the last line """
    last_line_index = f"{int(GUI_TERMINAL.text.index(tk.END).split('.')[0]) - 1}.0"
    GUI_TERMINAL.text.mark_set(tk.INSERT, last_line_index)  # Keep cursor on last line

# GUI setup
print("\nrunning FIDE...")

# create recents.txt
if not os.path.exists("recents.txt"):
    f = open("recents.txt", "x")
    f.close()

# ------- WIDGET -------- #

SEARCHING = None

#GUI TEXTBOX
GUI_TEXTBOX = tk.Text(APP, width=61, height=18, font=("Consolas 19"), undo=True, wrap="none", background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, insertbackground=FOREGROUND_COLOR)
GUI_TEXTBOX.place(rely=0, relx=0.037)
GUI_TEXTBOX.tag_config("GREEN", foreground="#41b196")
GUI_TEXTBOX.tag_config("PINK", foreground="#cba6f7")
GUI_TEXTBOX.tag_config("ORANGE", foreground="#f9e2af")
GUI_TEXTBOX.tag_config("BLUE", foreground="#386ed7")
GUI_TEXTBOX.tag_config("PURPLE", foreground="#634a7f")
GUI_TEXTBOX.tag_config("PINK", foreground="#e57bff")
GUI_TEXTBOX.tag_config("LIGHT_BLUE", foreground="#a5baaf")
GUI_TEXTBOX.tag_config("BOLD", font=("Consolas", 19, "bold"))
GUI_TEXTBOX.tag_config("ITALIC", font=("Consolas", 19, "italic"))
GUI_TEXTBOX.tag_config("HIGHLIGHT", background="blue")
GUI_TEXTBOX.config(spacing1=5)

# GUI LINE COUNTER
GUI_LINE_COUNTER = tk.Text(APP, width=3, height=18, font=("Consolas 19"), fg="lightblue", state="disabled", wrap="none", background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_LINE_COUNTER.place(rely=0, relx=0)
GUI_LINE_COUNTER.config(spacing1=5)

# GUI COMMAND HELP
GUI_COMMAND_HELP = tk.Text(APP,  font=("Consolas 14"), height=2, width=85, undo=True, state="disabled", bd=0, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_COMMAND_HELP.place(rely=0.951, relx=0.04, anchor= tk.W)
GUI_COMMAND_HELP.tag_config("help1", foreground="#41b196")
GUI_COMMAND_HELP.tag_config("help2", foreground="#cba6f7")
GUI_COMMAND_HELP.tag_config("help3", foreground="#386ed7")
GUI_COMMAND_HELP.tag_config("help4", foreground="#f9e2af")

# VARIABLE TEXTBOX
GUI_VARIABLE_BOX = tk.Text(APP, width=11, height=8, font=("Consolas 16"), background=BACKGROUND_COLOR)
GUI_VARIABLE_BOX.place(rely=0.105, relx=0.7511)
GUI_VARIABLE_BOX.config(state="disabled")

GUI_VARIABLE_LABEL = tk.Label(APP, text="║VARS║\n╚====╝", font=("Consolas 20 bold"), fg="lightblue", background=BACKGROUND_COLOR)
GUI_VARIABLE_LABEL.place(relx=0.77, rely=-0)

# FUNCTION TEXTBOX
GUI_FUNCTION_BOX = tk.Text(APP, width=11, height=8, font=("Consolas 16"), background=BACKGROUND_COLOR)
GUI_FUNCTION_BOX.place(rely=0.105, relx=0.887)
GUI_FUNCTION_BOX.config(state="disabled")

#GUI FUNCTION LABEL
GUI_FUNCTION_LABEL = tk.Label(APP, text="║FUNS║\n╚====╝", font=("Consolas 20 bold"), fg="lightblue", background=BACKGROUND_COLOR)
GUI_FUNCTION_LABEL.place(relx=0.905, rely=0)

# CONNECTION KEYS
VARS_CONNECTION_KEY = "[SENDING_VARS_TO_FIDE]"
FUNS_CONNECTION_KEY = "[SENDING_FUNS_TO_FIDE]"
INPUT_CONNECTION_KEY = "[RUNNING_IN_FIDE]"

# GUI TERMINAL
GUI_TERMINAL = InteractiveConsole(APP)
GUI_TERMINAL.place(relx=0.751, rely=0.53)

# GUI CLEAR/TERMINATE CONSOLE
GUI_CLEAR_CONSOLE = tk.Button(APP, text="×", fg="red", command = clear_console, font=("Consolas 15"), background=BACKGROUND_COLOR)
GUI_CLEAR_CONSOLE.place(relx=0.97, rely=0.4750,anchor=tk.CENTER)

# GUI CONSOLE LABEL
GUI_CONSOLE_LABEL = tk.Label(APP, text="║ CONSOLE ║\n╚=========╝", font=("Consolas 20 bold"), fg="lightblue", background=BACKGROUND_COLOR)
GUI_CONSOLE_LABEL.place(relx=0.81, rely=0.42)

# MENU BAR
GUI_MENUBAR = tk.Menu()
GUI_FILE_MENU = tk.Menu(GUI_MENUBAR, tearoff=False, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_FILE_MENU.add_command(label="New", accelerator="Ctrl+n", command=new_file)
GUI_FILE_MENU.add_command(label="Open", accelerator="Ctrl+o", command=open_file_from_dialog)

# RECENT FILES
GUI_RECENT_FILES_MENU = tk.Menu(GUI_FILE_MENU, tearoff=False, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_FILE_MENU.add_cascade(menu=GUI_RECENT_FILES_MENU, label="Open Recents")
GUI_FILE_MENU.add_command(label="Save", accelerator="Ctrl+s", command=save_file)
GUI_FILE_MENU.add_separator()
GUI_FILE_MENU.add_command(label="Exit", accelerator="Ctrl+e", command=exit)
GUI_MENUBAR.add_cascade(menu=GUI_FILE_MENU, label="File")

# GUI INSERT MENU
GUI_INSERT_MENU = tk.Menu(GUI_MENUBAR, tearoff=False, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_INSERT_MENU.add_command(label = "New Variable",  accelerator="Ctrl+Shift+v", command = insert_new_variable)
GUI_INSERT_MENU.add_command(label = "New Function",  accelerator="Ctrl+Shift+f", command = insert_new_function)
GUI_INSERT_MENU.add_command(label = "New For Loop",  accelerator="Ctrl+Alt+o", command = insert_new_for_loop)
GUI_INSERT_MENU.add_command(label = "New While Loop",  accelerator="Ctrl+Shift+w", command = insert_new_while_loop)
GUI_INSERT_MENU.add_command(label = "New If Else",  accelerator="Ctrl+Shift+I", command = insert_new_if_else)
GUI_MENUBAR.add_cascade(menu=GUI_INSERT_MENU, label="Insert")

# GUI RUN MENU
GUI_RUN_MENU = tk.Menu(GUI_MENUBAR, tearoff=False, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_RUN_MENU.add_command(label="Run", accelerator="F5", command=run_file)
GUI_MENUBAR.add_cascade(menu=GUI_RUN_MENU, label="Run")

# GUI CONFIGURATION MENU
GUI_CONFIGURATION_MENU = tk.Menu(GUI_MENUBAR, tearoff=False, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
GUI_CONFIGURATION_MENU.add_command(label = "Intepreter",  accelerator="Ctrl+i", command = interpreter_configuration)
GUI_CONFIGURATION_MENU.add_command(label = "Developer Mode ✗",  accelerator="Ctrl+d", command = developer_mode)
GUI_MENUBAR.add_cascade(menu=GUI_CONFIGURATION_MENU, label="Configure")

# MENU UPDATE
APP.config(menu=GUI_MENUBAR)

GUI_TOOL_MENU = tk.Menu(tearoff=False)
update_menu()
# assigning GUI_AUTOCOMPLETE to None, so it does not crash when trying to check if GUI_AUTOCOMPLETE exists
GUI_AUTOCOMPLETE = None
SELECTION = None
# Recents

update_recents()

# Line counter

update_line_counter()

# BINDINGS
APP.bind("<Control-n>", new_file)
APP.bind("<Control-o>", open_file_from_dialog)
APP.bind("<Control-s>", save_file)
APP.bind("<Control-e>", exit)
APP.bind("<F5>", run_file)
APP.bind("<Control-i>", interpreter_configuration)
APP.bind("<Control-d>", developer_mode)
APP.bind("<Control-V>", insert_new_variable)
APP.bind("<Control-F>", insert_new_function)
APP.bind("<Control-O>", insert_new_for_loop)
APP.bind("<Control-W>", insert_new_while_loop)
APP.bind("<Control-I>", insert_new_if_else)

APP.bind("<Control-space>", autocompletion)
APP.bind("<Control-q>", shuffle_complete_suggestions)
GUI_TEXTBOX.bind_all('<<Modified>>', check_autocompletion)
GUI_TEXTBOX.bind_all('<<Modified>>', update_text)
GUI_TEXTBOX.bind_all('<MouseWheel>', update_line_counter)
GUI_TEXTBOX.bind_all("<Key>", update_line_counter)
GUI_TEXTBOX.bind("<Button-3>", show_menu)

# ASSIGNING EVERY KEY FOR INPUT RESTRICTIONS 
for i in ["<Left>", "<Right>", "<Left>", "<Up>", '<Button-1>', '<Control-v>', '<Control-x>'] :
    GUI_TEXTBOX.bind(i, delete_autocomplete)
    GUI_TERMINAL.text.bind(i, restrict_input)
    
#MAIN LOOP
APP.mainloop()