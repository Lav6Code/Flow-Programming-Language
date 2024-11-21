"""

FLOW INTEGRATED DEVELOPMENT ENVIROMENT (for short FIDE)

"""


import tkinter as tk
from tkterminal import Terminal
import sv_ttk
from tkinter.filedialog import *
import importlib.util
import sys
import os
import time


# SETUP

WIDTH,HEIGHT = 1207,800
app = tk.Tk()
app.geometry(str(WIDTH)+"x"+str(HEIGHT))
app.lift()
app.title("untitled.flow")
app.resizable(True, True)
# FLOW SETUP

green_keywords = ['+', '*', "-", "/"]
red_keywords = ['var', 'output', "input", "if", "for","while","fetch","intersection","union","disjunction","superset","subset","len"]
orange_keywords = ["1","2","3","3","4","5","6","7","8","9","0",'"']
blue_keywords = [";","(",")"]
flow_path = "C:/Users/Valchichi/Dropbox/PROGRAMIRANJE/FLOW-programming language/FLOW.py"

# FUNCTIONSs

def highlight(keyword, tag_name):
    start = "1.0"
    
    while True:
        pos = textbox.search(keyword, start, stopindex=tk.END)
        end = f"{pos}+{len(keyword)}c"
        start = end
        if not pos:
            break

        #print(keyword, textbox.get(pos, end))
        
        if keyword == textbox.get(pos, end):
            textbox.tag_add(tag_name, pos, end)
    

def update_line_counter():
    global line_counter
    
    n = textbox.get("1.0",tk.END).count("\n")
    text = ""
    for i in range(n):
        text += f"{i+1}.\n"
    
    line_counter.config(state="normal")
    line_counter.delete('1.0', tk.END)
    line_counter.insert("1.0", text)
    line_counter.config(state="disabled")

def update_text(a=None):
    
    global line_counter

    textbox.tag_remove("GREEN", 1.0, tk.END)
    textbox.tag_remove("RED", 1.0, tk.END)
    textbox.tag_remove("BLUE", 1.0, tk.END)
    #print("UPDATING TEXT")
    
    for word in green_keywords:
        highlight(word, "GREEN")
    
    for word in red_keywords:
        highlight(word, "RED")
    
    for word in blue_keywords:
        highlight(word, "BLUE")
    
    for word in orange_keywords:
        highlight(word, "ORANGE")

    # INSIDE THE ""
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
    
    char_mapping = {
        
        "(":")",
        '"':'"',
        "[":"]",
        "{":"}"
        }
    
    if event.char in char_mapping.keys():
        current_position = textbox.index(tk.INSERT)
        textbox.insert(current_position, char_mapping[event.char])
        textbox.mark_set(tk.INSERT, current_position)
    
    update_text()
    
def focus_text_widget():
    textbox.focus_force()

def open_file(event=None):
    global file
    #print("TEXTBOX CONTENT IS THIS:"+textbox.get("1.0", tk.END))
    if textbox.get("1.0", tk.END).replace("\n","") == "":
        file = askopenfile(mode ='r', filetypes =[('Flow Files', '*.flow')])
        if file is not None:
            file_content = file.read()
            textbox.delete("1.0", tk.END)
            textbox.insert(tk.INSERT, file_content)
            update_text()
    else:
        response = tk.messagebox.askquestion(title="⚠️ File will not be saved! ⚠️", message="Save file before opening another file?",type="yesnocancel")
        if response == "yes":
            #print("SAVING")
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
            f.write(textbox.get("1.0",tk.END))
            file.close()
    else:
        file = asksaveasfile(defaultextension=".flow", filetypes=[("Flow files", "*.flow")])
        if file:    
            app.title(file.name.split("/")[-1])
            file.write(textbox.get("1.0", tk.END))
            file.close()

def new_file(event=None):
    if not textbox.get("1.0", tk.END).replace("\n","") == "":
        response = tk.messagebox.askquestion(title="⚠️ File will not be saved! ⚠️", message="Save file before creating a new file?",type="yesno")
        #print(response)
        if response == "yes":
            #print("SAVING")
            save_file()
            textbox.delete("1.0", tk.END)
            variable_box.delete("1.0", tk.END)
            app.update()
            file = None
        else:
            #print("NEW FILE")
            textbox.delete("1.0", tk.END)
            variable_box.delete("1.0", tk.END)
            app.update()
            file = None
    else:
        #print("NEW FILE")
        textbox.delete("1.0", tk.END)
        variable_box.delete("1.0", tk.END)
        app.update()
        file = None
        
def import_function_from_path(path_to_file, function_name):
    # Load the module from the file path
    spec = importlib.util.spec_from_file_location("module.name", path_to_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = module
    spec.loader.exec_module(module)
    
    # Retrieve the function from the module
    func = getattr(module, function_name)
    return func

def update_variables_textbox(variables):
    global variable_box
    variable_box.config(state="normal")
    variable_box.delete("1.0", tk.END)
    
    insert_text = ""
    
    for v in variables:
        insert_text += f"{v}={variables[v]}\n"
    variable_box.insert("1.0",insert_text)
    variable_box.config(state="disabled")

def run_file(event=None):
    global console, terminal
    save_file()
    if file:
        variable_box.delete(0, tk.END)
        terminal.run_command(f"python {flow_path} {file}")
        #update_variables_textbox(variables)
        

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
    
def toggle_debug(menu):

    global debug
    
    debug = not(debug)
    
    if debug == False:
        menu.entryconfigure(2, label="Debug ❌")
    else:
        menu.entryconfigure(2, label="Debug ✔️")
        
    app.update()
    time.sleep(0.1)

def exita(event=None):
    new_file()
    app.destroy()
    sys.exit()

def on_scrollbar(*args):
    # Synchronize the yview (vertical scrolling) of both textboxes
    textbox.yview(*args)
    line_counter.yview(*args)

def on_textscroll1(*args):
    # Scroll text2 when text1 is scrolled
    line_counter.yview_moveto(args[0])

def on_textscroll2(*args):
    # Scroll text1 when text2 is scrolled
    textbox.yview_moveto(args[0])

def console_input():
    global textbox

    textbox.delete("1.0", tk.END)

# TEXTBOX


BWIDTH,BHEIGHT=57,23
textbox = tk.Text(app, width =BWIDTH, height = BHEIGHT, font = ("Consolas 20"),yscrollcommand=on_textscroll1,undo=True)
textbox.place(rely=0,relx=0.04)
textbox.tag_config("GREEN", foreground="green") 
textbox.tag_config("RED", foreground="red") 
textbox.tag_config("ORANGE", foreground="orange") 
textbox.tag_config("BLUE", foreground="lightblue") 
textbox.config(spacing1=10)

VWIDTH,VHEIGHT=20,10
variable_box = tk.Text(app, width = VWIDTH, height=VHEIGHT,font = ("Consolas 20"))
variable_box.place(rely=0.082,relx=0.75171)
variable_box.config(state="disabled")

variable_label = tk.Label(app, text="║VARIABLES║\n╚=========╝", font = ("Consolas 20"), fg="lightblue")
variable_label.place(relx=0.81,rely=-0)

CWIDTH,CHEIGHT=40,10
terminal = Terminal(height=15, width = 35, font=("Consolas 11"))
terminal.shell = True
terminal.place(relx=0.751,rely=0.6)

console_label = tk.Label(app, text="║ CONSOLE ║\n╚=========╝", font = ("Consolas 20"), fg="lightblue")
console_label.place(relx=0.81,rely=0.5)

line_counter = tk.Text(app,width=3, height=23,font = ("Consolas 20"), fg="lightblue", state="disabled",yscrollcommand=on_textscroll2)
line_counter.place(rely=-0,relx=0)
line_counter.config(spacing1=10)

#MENU BAR
menubar = tk.Menu()
file = None

#FILE MENU
file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(label = "New",  accelerator="Ctrl+N", command = new_file)
file_menu.add_command(label = "Open", accelerator="Ctrl+O", command = open_file)
file_menu.add_command(label = "Save", accelerator="Ctrl+S", command = save_file)
file_menu.add_separator()
file_menu.add_command(label = "Exit", accelerator="Ctrl+E", command = exita)

#RUN FILE

run_menu = tk.Menu(menubar, tearoff=False)
run_menu.add_command(label = "Run",  accelerator="F5", command = run_file)


#CONFIGURE FILE

configuration_menu = tk.Menu(menubar, tearoff=False)
configuration_menu.add_command(label = "Intepreter",  accelerator="Ctrl + I", command = interpreter_configuration)
configuration_menu.add_command(label = "Debug ❌",  accelerator="Ctrl + D", command = lambda: toggle_debug(configuration_menu))

menubar.add_cascade(menu=file_menu, label="File")
menubar.add_cascade(menu=run_menu, label="Run")
menubar.add_cascade(menu=configuration_menu, label="Configuration")
app.config(menu = menubar)

# SHORTCUTS

app.bind("<Control-n>", new_file)
app.bind("<Control-o>", open_file)
app.bind("<Control-s>", save_file)
app.bind("<Control-e>", exita)

app.bind("<Control-i>", interpreter_configuration)
app.bind("<Control-d>", lambda: toggle_debug(configuration_menu))
app.bind("<F5>", run_file)
# LAST SETUP
debug = False
app.bind("<Key>", auto_finish)
words_to_highlight = []
sv_ttk.set_theme("dark")
app.after(1, focus_text_widget)
app.mainloop()