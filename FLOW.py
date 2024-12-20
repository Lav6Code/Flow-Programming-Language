import importlib.util
import sys

FLOW_VERSION = 0.1

FORBIDDEN_CHARS = ['~']

VARS = {}       
COMMANDS = [None, '+', '*', "-", "/", 
            ">", "<", "=", ">=", "<=", "!=", 
            'var', 'output', "input", "if", "for", "set",
            "num", "disjunction", "subset", "superset", "add", "union",
            "len", "fetch", "intersection"
            ]
COMMENT = "//"


def repeating_el(lists):
    non_repeating_elements = []
    for i in lists:
        if lists.count(i) == 1:
            non_repeating_elements.append(i)
    return list(set(non_repeating_elements))
        

def is_int(strs):
    if len(strs) == 0:
        return False
    isitint = True
    for i in strs:
        if i not in "0123456789":
            isitint = False
            break
    return isitint

def import_function_from_path(path_to_file, function_name):
    # Load the module from the file path
    spec = importlib.util.spec_from_file_location("module.name", path_to_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = module
    spec.loader.exec_module(module)
    
    # Retrieve the function from the module
    func = getattr(module, function_name)
    return func

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
            if COMMANDS.count(self.com) == 0:
                print(f"SYNTAX ERROR: '{command}' is not a command or a variable.")
                exit()
        else: 
            
            # is it BLK?
            nr_coms = 0
            for a in arg:
                if type(a) == Token and a.typ == "COM":
                    nr_coms += 1
            if nr_coms == len(arg):
                self.typ = "BLK"
        
            elif ";" in argstr[0]:
                self.typ = "BLK"
                
            elif is_int(argstr[0]):
                self.typ = "NUM"
            
            elif '"' in argstr[0]:
                self.typ = "TXT"
                    
            elif '"' not in argstr[0]:
                self.typ = "VAR"


        if self.typ is None:
            print(f'error in Token {self.dsc}')
            print("SYNTAX ERROR: wrong type declaration")
        
        # print('  ...created', self)
            
            
    def __repr__(self):
        return f"{self.typ} Token {self.dsc} (sol: {self.sol})"
        
    
    def evaluate(self, forced=False):
        
        # if not self.sol:
            
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
            if self.com in COMMANDS:
                self.sol = execute(self.com, self.arg)
    
        elif self.typ == "BLK" and forced:
            for a in self.arg:
                a.evaluate()
            self.sol = True # execute(None, self.arg)


def parse_arg(sstr):
    
    # print(f'...parsing args: {sstr}')

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
    
    # print(f'...parsed args: {"".join(sstr).split("~")}')
    
    return "".join(sstr).split("~")
    
    
def parse_block(sstr):
    
    # print(f'...parsing block: {sstr}')
    
    bracket_checkup = 0 
    separations = []

    for i,c in enumerate(sstr):
        
        if c == "(":
            bracket_checkup += 1
        elif c == ")":
            bracket_checkup -= 1
        
        if bracket_checkup == 0:
            if c == ";":
                separations.append(i)

    sstr = list(sstr)

    for p in separations:
        if p != len(sstr) - 1:
            sstr[p] = "~"
    
    # print(f'...parsed block as: {"".join(sstr).split("~")}')
    
    return "".join(sstr).split("~")


def execute(command, args): # args with ,
    global VARS
    # argstr = []
    # for a in args:
    #     argstr.append(a.sol)
        
    # Operators
    if command == "+":
        if type(args[0].sol) == str:
            return (args[0].sol) + (args[1].sol)
        if type(args[0].sol)==int and type(args[1].sol)==int:
            return int(args[0].sol) + int(args[1].sol)
        else:
            print("ARGUMENT ERROR: Trying to add(+) two values with different type.")
            exit()

    elif command == "*":
        if is_int(args[0].sol) and is_int(args[1].sol):
            return int(args[0].sol) * int(args[1].sol)
        else:
            print("ARGUMENT ERORR: Trying to multiply(*) two values with wrong type.")
            exit()

    elif command == "-":
        if is_int(args[0].sol) and is_int(args[1].sol):
            return int(args[0].sol) - int(args[1].sol)
        else:
            print("ARGUMENT ERORR: Trying to substract(-) two values with wrong type.")
            exit()

    elif command == ">":
        if type(args[0].sol) == int and type(args[0].sol) == int:
            return args[0].sol > args[1].sol
        else:
            print("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM")
            exit()

    elif command == ">=":
        if type(args[0].sol) == int and type(args[0].sol) == int:
            return args[0].sol >= args[1].sol
        else:
            print("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM")
            exit()

    elif command == "<":
        if type(args[0].sol) == int and type(args[0].sol) == int:
            return args[0].sol < args[1].sol
        else:
            print("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM")
            exit()

    elif command == "<=":
        if type(args[0].sol) == int and type(args[0].sol) == int:
            return args[0].sol <= args[1].sol
        else:
            print("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM")
            exit()

    elif command == "=":
        if type(args[0].sol) == int and type(args[0].sol) == int:
            return args[0].sol == args[1].sol
        else:
            print("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM")
            exit()

    elif command == "!=":
        if type(args[0].sol) == int and type(args[0].sol) == int:
            return args[0].sol != args[1].sol
        else:
            print("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM")
            exit()
    
    # Loops Ifs Elifs Whiles
    
    elif command == "if":
        if args[0].sol == True:
            args[1].evaluate(forced=True)
    
    elif command == "for":
        if type(args[0].sol) == int:
            for i in range(args[0].sol):
                args[1].evaluate(forced=True)
        else:
            print("ARGUMENT ERROR: Trying to use non NUM value for FOR loop.")
            exit()

    elif command == "while":
        if args[0].typ == "BLK":
            while True:
                TOKENS = []
                token_root = tokenize(args[0].dsc, TOKENS)
                token_root.evaluate(forced=True)
                if token_root.sol == True:
                    args[1].evaluate(forced=True)
                else:
                    break
        else:
            print("ARGUMENT ERROR: Trying to execute a argument that does not have the abilty to be intepreted.")
            exit()
    # Other commands

    elif command == "output":
        print(args[0].sol)
        return True
    
    elif command == "fetch":
        if len(args) == 2:
            set_ = args[0].sol
            i_ = int(args[1].sol)
            try:
                return set_[i_]
            except:
                print(f"INDEX ERROR: trying to FETCH inexistent value at {i_} position in {set_} SET.")
                exit()
        elif len(args) == 3:
            set_ = args[0]
            i_ = args[1].sol
            j_ = args[2].sol
            try:
                return set_.sol[i_:j_]
            except:
                print(f"INDEX ERROR: trying to FETCH inexistent value from {i_} position to {j_} in {set_} SET.")
                exit()

    elif command == "add":
        if type(args[0].sol) == list:
            if len(args) == 2:
                SET_UPDATED = args[0].sol
                SET_UPDATED.append(args[1].sol)
                VARS[args[0].dsc] = SET_UPDATED
            else:
                SET_UPDATED = args[0].sol
                SET_UPDATED.insert(args[1].sol, args[2].sol)
                VARS[args[0].dsc] = SET_UPDATED
        else:
            print(f"ARGUMENT ERROR: trying to add an element into a wrong TYPE, should be SET")
            exit()

    elif command == "union":
        UNION_SET = []
        for a in args:
            if type(a.sol) == list:
                UNION_SET += a.sol
            else:
                print("ARGUMENT ERROR: trying to unionize elements that are wrong TYPE, both elements should be SET")
                exit()
        UNION_SET = list(set(UNION_SET))
        return UNION_SET
    
    elif command == "len":
        if type(a.sol) == list:
            return len(a.sol)
        else:
            print("ARGUMENT ERROR: Trying to get a lentgh of a wrong type, should be SET.")
            exit()

    elif command == "intersection":
        INTERSECTED = []
        if type(args[0].sol) == list and type(args[1].sol) == list:
            for E1 in args[0].sol:
                for E2 in args[1].sol:
                    if E1 == E2:
                        INTERSECTED.append(E1)
            return list(set(INTERSECTED))
        else:
            print("ARGUMENT ERROR: trying to intersect elements that are wrong TYPE, both elements should be SET")
            exit()

    elif command == "subset":
        if type(args[0].sol) == list and type(args[1].sol) == list:
            #QUICK CHECK
            if len(args[0].sol) > len(args[1].sol):
                return False
            
            strS1 = "".join(str(x) for x in args[0].sol)
            strS2 = "".join(str(x) for x in args[1].sol)  
            if strS1 in strS2: return True
        else:
            print("ARGUMENT ERROR: trying to detect subsets of elements that are wrong TYPE, both elements should be SET")
            exit()
        return False
    
    elif command == "superset":
        if type(args[0].sol) == list and type(args[1].sol) == list:
            #QUICK CHECK
            if len(args[1].sol) > len(args[0].sol):
                return False
            
            strS1 = "".join(str(x) for x in args[0].sol)
            strS2 = "".join(str(x) for x in args[1].sol)  
            if strS2 in strS1: return True
        else:
            print("ARGUMENT ERROR: trying to detect subsets of elements that are wrong TYPE, both elements should be SET")
            exit()
        return False
    
    elif command == "disjunction":
        if type(args[0].sol) == list and type(args[1].sol) == list:
            
            a = repeating_el(args[0].sol + args[1].sol)
            return a
            
        else:
            print("ARGUMENT ERROR: trying to disjunct of elements that are wrong TYPE, both elements should be SET")
            exit()
        return False

    elif command == "input":
        a = input()
        if a != "":
            return a
        else:
            return args[0].sol

    elif command == "var":
        VARS[args[0].sol] = args[1].sol
        return True
    
    # Type conversions:
        
    elif command == "num":
        if is_int(args[0].sol):
            return int(args[0].sol)
        else:
            print("TYPE ERROR: Error while handling conversion from this argument's type to NUM type")
            exit()

    elif command == "set":
        lst = []
        for a in args:
            lst.append(a.sol)
        return lst
    
    #COMMAND NOT FOUND SYNTAX ERROR
    elif command not in COMMANDS:
        print(f"SYNTAX ERROR: {command} is not a command or a variable.")
        exit()
    
    
def tokenize(code, tokens_list=None):
    
    # f' - tokenizing: {code}')

    first_bracket = None
    last_bracket = None
    
    for i,e in enumerate(code):
        
        i1 = len(code) - i - 1
        
        if e == "(" and first_bracket is None:
            first_bracket = i
            
        if code[i1] == ")" and last_bracket is None:
            last_bracket = i1
            
    # FIX CHECKING FOR ERROR IN BRACKETS
    if code.count("(")!=code.count(")"):
            print('SYNTAX ERROR: brackets are not balanced')
            exit()
    
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

    if command is None and ';' in arg:  # it's a block
        if arg[-1] == ';':
            arg = arg[:-1]
        arg = parse_block(arg)
    else:                               # it's a command
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
            

def run(file_path):
    global VARS, FIDE_PATH
  
    EXECUTE_MESSAGE =f"Flow v{FLOW_VERSION} running, {file_path.split('/')[-1]}"

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
    file = file.replace("\t", "")
    
    # Execute program
    TOKENS = []
    token_root = tokenize(file, TOKENS)
    token_root.evaluate(forced=True)
 
    return VARS, EXECUTE_MESSAGE


# RUNNING

# Check if a .flow file is provided as an argument
if len(sys.argv) < 3:
    print("Usage: python flow.py <filename>.flow")
    sys.exit(1)

# Get the filename from the command line
filename = sys.argv[1]
RUNNER = sys.argv[2]
VARS_CONNECTION_KEY = "[SENDING_VARS_TO_FIDE]"
INPUT_CONNECTION_KEY = "[RUNNING_IN_FIDE]"

run(filename)

# sending vars to FIDE
if RUNNER == "FIDE":
    print(VARS_CONNECTION_KEY+str(VARS))
