FLOW_VERSION = 0.1

FORBIDDEN_CHARS = ['~']

VARS = {}
COMMANDS = [None, '+', '*', "-", "/", 
            ">", "<", "=", ">=", "<=", "!=", 
            'var', 'output', "input"]
COMMENT = "//"



def is_int(strs):
    if len(strs) == 0:
        return False
    isitint = True
    for i in strs:
        if i not in "0123456789":
            isitint = False
            break
    return isitint


class Token:
    
    def __init__(self, command, arg):

        # print(f'- creating token with {command=}, {arg=}')

        self.com = command
        self.arg = arg  # list
        
        argstr = []
        for a in arg:
            if type(a) == Token:
                argstr.append(a.dsc)
            elif type(a) == str:
                argstr.append(a)
        if self.com:
            self.dsc = command + "(" + ','.join(argstr) + ")"
        else:
            self.dsc = ';'.join(argstr)
            
        self.sol = None
        self.typ = None
        
        if self.com:
            self.typ = "COM"
            
        else: 
            
            # is it BLK?
            nr_coms = 0
            for a in arg:
                if type(a) == Token and a.typ == "COM":
                    nr_coms += 1
            if nr_coms == len(arg):
                self.typ = "BLK"
                
            # check of other non-COM types
        
            elif ";" in argstr[0]:
                self.typ = "BLK"
                
            elif is_int(argstr[0]):
                self.typ = "NUM"
            
            elif '"' in argstr[0]:
                self.typ = "TXT"
                    
            elif '"' not in argstr[0]:
                self.typ = "VAR"
            
            elif "[" in argstr[0] and "]" in argstr[0]:
                self.typ = "SET"
            
        if self.typ is None:
            print(f'error in Token {self.dsc}')
            raise Exception("SYNTAX ERROR: wrong type declaration")
        
        # print('  ...created', self)
            
            
    def __repr__(self):
        return f"{self.typ} Token {self.dsc} (sol: {self.sol})"
        
    
    def evaluate(self):
        
        if not self.sol:
            
            if self.typ == "NUM": 
                if is_int(self.arg[0]):
                    self.sol = int(self.arg[0])
                    
            elif self.typ == "TXT":
                self.sol = self.arg[0][1:-1]
                    
            elif self.typ == "VAR":
                self.sol = VARS[self.arg[0]]
                
            elif self.typ == "COM":
                for a in self.arg:
                    a.evaluate()
                self.sol = execute(self.com, self.arg)
                  
            elif self.typ == "BLK": 
                for a in self.arg:
                    a.evaluate()
                self.sol = True # execute(None, self.arg)


def parse_arg(sstr):
    
    if ";" in sstr:
        # it's a block
        args = sstr.split(";")
        return args[:-1]
        
    bracket_checkup = 0 
    separations = []
    
    for i,c in enumerate(sstr):
        
        if c == "(":
            bracket_checkup += 1
        elif c == ")":
            bracket_checkup -= 1
        
        if bracket_checkup == 0:
            if c == ",":
                separations.append(i)

    sstr = list(sstr)

    for p in separations:
        sstr[p] = "~"
            
    return "".join(sstr).split("~")


def execute(command, args): # args with ,

    global VARS

    argstr = []
    for a in args:
        argstr.append(a.sol)
        
    # Operators

    if args == []:
        argstr = [None]

    if command == "+":
        return int(argstr[0]) + int(argstr[1])
    
    elif command == "*":
        return int(argstr[0]) * int(argstr[1])
    
    elif command == "-":
        return int(argstr[0]) - int(argstr[1])
 
    elif command == ">":
        return argstr[0] > argstr[1]
    elif command == ">=":
        return argstr[0] >= argstr[1]
    elif command == "<":
        return argstr[0] < argstr[1]
    elif command == "<=":
        return argstr[0] <= argstr[1]
    elif command == "=":
        return argstr[0] == argstr[1]
    elif command == "!=":
        return argstr[0] != argstr[1]

    # Other commands

    elif command == "output":
        if args[0].typ == "TXT":
            print(argstr[0])
        else:
            print(argstr[0])
        return True

    elif command == "input":
        if args[0].typ == "TXT":
            return input(argstr[0])
        else:
            return input(argstr[0])

    elif command == "var":
        VARS[argstr[0]] = argstr[1]
        return True
    
    """
    elif not command:  # executing code
        code = args[0]
        code_prep = code
        
        #SPLITTING THE LINE
        
        b_counter = 0
        for i,l in enumerate(code):
            if l == "(":
                b_counter += 1
            elif l == ")":
                b_counter -= 1
        
            if l == ";" and b_counter == 0:
                code_prep = list(code_prep)
                code_prep[i] = '~'
                code_prep = "".join(code_prep)

        code_prep = code_prep.split('~')
        
        for line in code_prep:
            if len(line) != 0 and not line.startswith(COMMENT):
                execute(None, line)
                
                print('\n*** interpreting line:', line)
        
        return True
    """
        

def tokenize(code, tokens_list=None):
    
    # print(f' - tokenizing: {code}')

    first_bracket = None
    last_bracket = None
    
    for i,e in enumerate(code):
        
        i1 = len(code) - i - 1
        
        if e == "(" and first_bracket is None:
            first_bracket = i
            
        if code[i1] == ")" and last_bracket is None:
            last_bracket = i1
            
    # FIX CHECKING FOR ERROR IN BRACKETS
    assert (type(first_bracket) == int and type(last_bracket) == int) \
            or not (first_bracket and last_bracket), \
            'SYNTAX ERROR: BRACKETS NOT OK'
    
    # print(f'brackets: {first_bracket}, {last_bracket}')
    if not first_bracket and not last_bracket:
        # value
        command = None
        arg = code
        
    elif first_bracket == 0 and last_bracket == len(code) - 1:
        # code
        command = None
        arg = code[1:-1]
        first_bracket = True
        last_bracket = True
        
    else:
        # command
        arg = code[first_bracket+1:last_bracket]
        command = code[:first_bracket]
        
    # print(f'{command=}')

    # arg = arg.split(",")
    arg = parse_arg(arg)
        
    if command is None and not (first_bracket and last_bracket):  # done?
        token = Token(command, arg)
        
        if tokens_list is not None:
            tokens_list.append(token)
            
        return token
    
    arg_tokens = []
    for a in arg:      
        arg_tokens.append(tokenize(a, tokens_list))

    token = Token(command, arg_tokens)
    
    if tokens_list is not None:
        tokens_list.append(token)

    return token
            

def run(file_path, debug):
  
    print(f'\n\nFlow v{FLOW_VERSION}\nrunning', file_path)
    
    file = open(file_path)
    file = file.read()
    file = '(' + file + ')'
    
    # Removing " " in file
    n_catcher = 0
    i_spaces = []
    for i,f in enumerate(file):
        if  f == '"':
            n_catcher += 1
            if n_catcher == 2:
                n_catcher = 0

        if n_catcher==0 and f == " ":
            i_spaces.append(i)
    
    file = list(file)
    for i in i_spaces:
        file[i] = "~"
    file = "".join(file)
    file = file.replace("~", "")
    
    # Additional cleanup
    file = file.replace("\n", "")
    
    # Execute program
    TOKENS = []
    token_root = tokenize(file, TOKENS)
    token_root.evaluate()
    
    if debug:
        
        print("_____________ VARIABLES ______________")
        
        for var, val in VARS.items():
            print(f"{var}={val}")
            
        print("_____________ TOKENS ______________")
        
        for t in TOKENS:
            print(t)
    
        print("_____________PROGRAM ENDED______________")
