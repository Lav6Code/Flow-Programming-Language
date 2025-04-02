# Imports
import sys
import math
import random
from copy import deepcopy
import draw as d


FLOW_VERSION = "1.0"

DEVELOPER_MODE = False

FORBIDDEN_CHARS = ['~']

VARS = {"pi": 3.1415926535}       
FUNS = {}
# Commands
# Same as in the FIDE.py
COMMANDS = [None,
            '+', '*', "-", "/", "sum", "random",  # MATH
            ">", "<", "=", ">=", "<=", "!=", "max", "min", "not", "and", "or", "xor", # LOGIC
            'output', "input", # USER INTERACTION
            "if", "for", "while", "loop", "seq",  # FLOW
            "set", 'var', # OBJECT CREATIONS
            "lower", "upper", "trim", "replace", #TXT MANAGMENT
            "num", "txt",  #TYPES
            "disjunction", "subset", "superset", "add", "union", "sort", "reverse", "filter", "remove", "setify", # SET RELATED
            "len", "fetch", "intersection",  # SET RELATED
            "func", "call", "draw", # FUNCTION RELATED
            "Triangle", "Line", "Circle", "Polyline", "Rectangle", "InCircle", "CircumCircle", "rotate" ,"Point", "Polygon", "Graph", "get_x", "translate" , "get_y", "Vector",  #GEOMETRY
            "get", "object", "attr" # OBJECT RELATED
            ]
BOOLS = ["TRUE", "FALSE"]

COMMENT = "$"

# Functions
def repeating_el(lists):
    non_repeating_elements = []
    for i in lists:
        if lists.count(i) == 1:
            non_repeating_elements.append(i)
    return list(set(non_repeating_elements))
        
def is_int(s):
    try:
        float(s)  # Try converting to a float
        return True
    except ValueError:
        return False

class Token:
    
    def __init__(self, command, arg):

        if DEVELOPER_MODE:
            print(f'DEBUG: creating token with {command=}, {arg=}')

        self.arg = arg  # list
        self.com = command
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
        # this is needed for BLK
        nr_coms = 0
        for a in arg:
            if type(a) == Token and a.typ == "COM":
                nr_coms += 1
        
        if self.com: # command type case
            self.typ = "COM"

        elif argstr[0][0] == '"' and argstr[0][-1] == '"': # txt type case
            self.typ = "TXT"
        
        elif is_int(argstr[0]): # num type case
            self.typ = "NUM"

        elif ';' in argstr[0] or nr_coms == len(arg): # blk type case
            self.typ = "BLK"
        
        elif argstr[0] in BOOLS: # bln type case
            self.typ = "BLN"

        elif '"' not in argstr[0]: # var type case
            self.typ = "VAR"

        else: 
            raise_error(f'SYNTAX ERROR: {self.dsc} is not a legal FLOW code structure.', self) # typ not recognized

        if DEVELOPER_MODE:
            print('DEBUG:  ...created', self)    
     
            
    def __repr__(self):
        return f"{self.typ} Token {self.dsc} (sol: {self.sol})"
        
    
    def evaluate(self, forced=False):

        global VARS

        #print(f'...evaluating {self}')
            
        if self.typ == "NUM": 

            if is_int(self.arg[0]):
                if "." in self.arg[0]:
                    self.sol = float(self.arg[0])
                else:
                    self.sol = int(self.arg[0])
                
        elif self.typ == "TXT":
            self.sol = self.arg[0][1:-1]
                
        elif self.typ == "VAR":
            if self.arg[0] in VARS:
                self.sol = VARS[self.arg[0]]
            else:
                raise_error(f'SYNTAX ERROR: {self.dsc} is not recognized as any FUNCTION, VARIABLE or COMMAND', self)

        elif self.typ == "COM":
            for a in self.arg:
                a.evaluate()
            if self.com in COMMANDS:
                self.sol = execute(self)

        elif self.typ == "BLK" and forced:
            
            for a in self.arg:
                a.evaluate()
        
        elif self.typ == "BLN":
            if self.arg[0] in BOOLS: # IT NEEDS TO BE FOR SAFETY PURPOSES
                self.sol = eval(self.arg[0].lower().capitalize())
            else:
                raise_error(f'SYNTAX ERROR: {self.dsc} is not recognized as any FUNCTION, VARIABLE or COMMAND', self)

def raise_error(erorr_msg, token=False):
    print(erorr_msg)
    if token:
        print(f"ERROR FOUND IN {token.dsc}")
    exit()
    

def parse_arg(sstr):

    bracket_checkup = 0 
    inside_qoutes = False
    separations = []
    if "" in sstr.split(","): # New added (check if it breaks anything)
        raise_error(f"ARGUMENT ERROR: Sufficient number of , in {sstr}")
    
    for i,c in enumerate(sstr):
        
        if c == "(": # inside brackets
            bracket_checkup += 1
        elif c == ")": # outside brackets
            bracket_checkup -= 1
        
        if c == '"':
            inside_qoutes = not(inside_qoutes)
        
        if bracket_checkup == 0 and not(inside_qoutes):
            if c == ",":
                separations.append(i)

    sstr = list(sstr)

    # adding sepration marks
    for p in separations:
        sstr[p] = "~"

    # splitting on sepration marks    
    return "".join(sstr).split("~")
    
    
def parse_block(sstr):
    
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
    
    return "".join(sstr).split("~")


def execute(token):
    global VARS, FUNS
    command = token.com
    args = token.arg
    # Objects
    if command == "object":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments", token)
        
        if args[0].sol in COMMANDS:
            raise_error("ARGUMENT ERROR: Object can't be named after a built in command", token)

        if type(args[0].sol) == str:
            objs = {"name":str(args[0].sol)}
            return objs
        else:
            raise_error("ARGUMENT ERROR: Error while settings objects name attribute, it should be TXT", token)

    elif command == "draw":
        for i in args:
            if type(i.sol) != dict:
                raise_error("ARGUMENT ERROR: draw command only takes in objects", token)

        argsol = []
        for i in args: argsol.append(i.sol)
        sys.stdout.flush()
        d.start(argsol)

    elif command == "Circle":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments", token)
        if type(args[0].sol) in [dict, list] and type(args[1].sol) in  [int, float]:

            if type(args[0].sol) == dict:
                center = [args[0].sol["x"], args[0].sol["y"]]
            else:
                center = args[0].sol

                for i in args[0].sol:
                    if is_int(i):
                        ...
                    else:
                        raise_error("ARGUMENT ERROR: Circle commands takes in a list of only NUM type values",token)

            objc = {"name":"Circle",
                    "center":center,
                    "radius":args[1].sol,
                    "diameter": args[1].sol*2,
                    "perimeter": args[1].sol*2*math.pi,
                    "area": args[1].sol**2*math.pi}
            return objc
        
    elif command == "Graph":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments", token)
        if type(args[0].sol) in  [int, float] and type(args[1].sol) in  [int, float]:
            slope = args[0].sol
            intercept = args[1].sol
            dot_one = (0, slope*0 + intercept)
            dot_two = (1, slope*1 + intercept)
            
            objc = {"name":"Graph",
                    "points":[dot_one, dot_two],
                    "function": f"y={slope}x+{intercept}",
                    "slope":slope,
                    "intercept":intercept}
            return objc
        else:
            raise_error("ARGUMENT ERROR: Both arguments in Graph() command should be NUM", token)
    
    elif command == "Point":
        if not(type(args[0].sol) in [int, float] and type(args[1].sol) in [int, float]):
            raise_error("ARGUMENT ERROR: Wrong argument type")
        return {"name": "Point", "x":args[0].sol, "y":args[1].sol}

    elif command == "Polygon":
        points = []
        for i in args: 
            if isinstance(i.sol, list):
                if len(i.sol) == 2:
                    for j in i.sol:
                        if not isinstance(j, (int, float)):
                            raise_error("ARGUMENT ERROR: Trying to create a Polygon object with points whose X, Y coordinates are not num type.", token)
                    points.append([i.sol[0], i.sol[1]])
                else:
                    raise_error("ARGUMENT ERROR: Length of every set used in creating Polygon object needs to be 2", token)
            elif isinstance(i.sol, dict):
                if i.sol.get("name") == "Point":  # Use .get() to avoid KeyError
                    if "x" in i.sol and "y" in i.sol:
                        points.append([i.sol["x"], i.sol["y"]])
                    else:
                        raise_error("ARGUMENT ERROR: Point object is missing 'x' or 'y' key.", token)

        # Making the object's atributes
        # Sides
        sides = []
    
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]  # Connect to the next point, and wrap around
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            sides.append(distance)
        
        n = len(points)
        area = 0
    
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]  # Wrap around to the first point
            area += x1 * y2 - y1 * x2
        area = abs(area/2)

        return {
                "name":"Polygon", 
                "points":points,
                "sides":sides,
                "area":area, 
                "perimeter":sum(sides)
                }
    
    elif command == "rotate":
        if type(args[0].sol) == dict:
            if "points" in args[0].sol:

                if len(args) == 3:
                    if type(args[1].sol) == dict:
                        if "x" in args[1].sol.keys() and "y" in args[1].sol.keys():
                            cx,cy = [args[1].sol["x"], args[1].sol["y"]]


                    elif type(args[1].sol) == list:
                        if len(args[1].sol) == 2:
                            if type(args[1].sol[0]) == int and type(args[1].sol[1]) == int:
                                cx, cy = args[1].sol
                    else:
                        raise_error("ARGUMENT ERROR: Second argument in rotate function is not Point obj or set",token)
                    points = args[0].sol["points"]
                    if type(args[2].sol) == int:
                        angle = args[2].sol
                    else:
                        raise_error("ARGUMENT ERROR: Third argument")

                elif len(args) == 2:
                    cx = sum(e[0] for e in args[0].sol["points"]) // len(args[0].sol["points"])
                    cy = sum(e[1] for e in args[0].sol["points"]) // len(args[0].sol["points"])
                    if type(args[1].sol) == int:
                        angle = args[1].sol
                    else:
                        raise_error("ARGUMENT ERROR: Third argument")
                    points = args[0].sol["points"]

                updated_points = []
                for i in points:
                    x,y = i
                    radians = math.radians(angle)
                    cos_theta = math.cos(radians)
                    sin_theta = math.sin(radians)
                    # Translate point to origin
                    x -= cx
                    y -= cy
 
                    # Rotate around origin
                    x_new = x * cos_theta - y * sin_theta
                    y_new = x * sin_theta + y * cos_theta
                    updated_points.append([x_new+cx, y_new+cy])
                    
            else:
                raise_error("ARGUMENT TYPE: Inavlid obj format")
        else:
            raise_error("ARGUMENT TYPE: First argument of rotate command should be OBJ")

        new_obj = deepcopy(args[0].sol)

        new_obj["points"] = updated_points

        return new_obj



    elif command == "translate":
        
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Insufficent number of arguments", token)

        if type(args[0].sol) != dict and type(args[1].sol) != dict:
            raise_error("ARGUMENT ERROR: Wrong argument type, should be OBJ", token)

        if "name" not in args[0].sol.keys():
            raise_error("ARGUMENT ERROR: Object is not valid for this operation", token)

        if args[0].sol["name"] in ["Vector", "Graph"]:
            raise_error("ARGUMENT ERROR: Wrong object used as an argument", token)

        if type(args[1].sol) != dict:
            raise_error("ARGUMENT ERROR: Second argument should be a Vector OBJ",token)

        if "name" not in args[1].sol.keys():
            raise_error("ARGUMENT ERROR: Object is not valid for this operation", token)
        
        if args[1].sol["name"] != "Vector":
            raise_error("ARGUMENT ERROR: Wrong object used as an argument", token)

        if "end" not in args[1].sol.keys():
            raise_error("ARGUMENT ERROR: end attribute is not inside the Vector object")

        vect = args[1].sol["end"]
        dx, dy = vect[0], vect[1]

        new_obj = deepcopy(args[0].sol)
        
        if new_obj["name"] != "Circle":
            for i in range(len(new_obj["points"])):
                new_obj["points"][i][0] += dx
                new_obj["points"][i][1] += dy
        else:
            new_obj["center"][0] += dx
            new_obj["center"][1] += dy
        return new_obj

    elif command == "get_x":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments", token)
        
        if type(args[0].sol) == dict:
            if "name" in args[0].sol.keys():
                if args[0].sol["name"] == "Graph":
                    if type(args[1].sol) in [int, float]:
                        if "slope" in args[0].sol.keys() and "intercept" in args[0].sol.keys():
                            a = args[0].sol["slope"]
                            b = args[0].sol["intercept"]
                            y = args[1].sol

                            if not isinstance(y, (int, float)):
                                raise_error("ARGUMENT ERROR: 'y' must be a number.", token)

                            x = (y - b) / a  # Corrected formula
                            return x

                        else:
                            raise_error("ARGUMENT ERROR: Object is not valid for this operation", token)
                    else:
                        raise_error("ARGUMENT ERROR: Wrong argument type, should be NUM", token)
                else:
                    raise_error("ARGUMENT ERROR: Object should has a name attribute that is Graph", token) 
            else:
                raise_error("ARGUMENT ERROR: Object is not valid for this operation", token)
        else:
            raise_error("ARGUMENT ERROR: First argument should be OBJ.", token)
    
    elif command == "get_y":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments", token)
        if type(args[0].sol) == dict:
            if "name" in args[0].sol.keys():
                if args[0].sol["name"] == "Graph":
                    if type(args[1].sol) in [int, float]:
                        if "slope" in args[0].sol.keys() and "intercept" in args[0].sol.keys():
                            a = args[0].sol["slope"]
                            b = args[0].sol["intercept"]
                            x = args[1].sol
                            y = a*x+b
                            return y
                        else:
                            raise_error("ARGUMENT ERROR: Object is not valid for this operation", token)
                    else:
                        raise_error("ARGUMENT ERROR: Wrong argument type, should be NUM", token)
                else:
                    raise_error("ARGUMENT ERROR: Object should has a name attribute that is Graph", token) 
            else:
                raise_error("ARGUMENT ERROR: Object is not valid for this operation", token)
        else:
            raise_error("ARGUMENT ERROR: First argument should be OBJ.", token)

    elif command == "Triangle":
        points = []
        
        if len(args) != 3:
            raise_error("ARGUMENT ERROR: Number of points required to create a Triangle is be 3.", token)

        for i in args: 
            if type(i.sol) == list: 
                for j in i.sol:
                    if type(j) not in [int, float]:
                        raise_error("ARGUMENT ERROR: Trying to create a Triangle object with points which X, Y coordinated are not num type.", token)  
                points.append([i.sol[0], i.sol[1]])
            elif type(i.sol) == dict:
                if "name" in i.sol.keys() and "x" in i.sol.keys() and "y" in i.sol.keys():
                    if i.sol["name"] == "Point":
                        points.append([i.sol["x"], i.sol["y"]])
                    else:
                        raise_error("ARGUMENT ERROR: name attribute should be Point", token)
                else:
                    raise_error("ARGUMENT ERROR: name,x,y attributes should be inside the Point attribute", token)
            else:
                raise_error("ARGUMENT ERROR: Trying to create a Triangle object, wrong arguments, should be sets points (X,Y positions) or Point OBJ.", token)

        # Making the object's atributes
        # Sides
        sides = []
    
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]  # Connect to the next point, and wrap around
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            sides.append(distance)

        # Area
        area = 0
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            area += x1 * y2 - y1 * x2
        area = abs(area)/2

        return {
                "name":"Triangle", 
                "points":points,
                "sides":sides,
                "area":area, 
                "perimeter":sum(sides)
                }

    elif command == "Line":
        points = []
        for i in args: 
            if type(i.sol) == list: 
                for j in i:
                    if type(j) != int:
                        
                        raise_error("ARGUMENT ERROR: Trying to create a Line object with points which X, Y coordinated are not num type.", token)    
                    points.append[[i[0], i[1]]]
            elif type(i.sol) == dict:
                if "name" in i.sol.keys() and "x" in i.sol.keys() and "y" in i.sol.keys():
                    if i.sol["name"] == "Point":
                        points.append([i.sol["x"], i.sol["y"]])
                    else:
                        raise_error("ARGUMENT ERROR: name attribute should be Point", token)
                else:
                    raise_error("ARGUMENT ERROR: name,x,y attributes should be inside the Point attribute", token)
            else:
                raise_error("ARGUMENT ERROR: Trying to create a Line object, wrong arguments, should be 2 sets that represent points (x,y)", token)

        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Number of points required to create a Line is be 2.", token)
        
        obj = {"name":"Line"}
        x1, y1 = points[0]
        x2, y2 = points[1]
        c = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        obj["length"] = c
        obj["points"] = points

        return obj

    elif command == "Rectangle":
        points = []
        for i in args: 
            if type(i.sol) == list: 
                for j in i.sol:
                    if type(j) != int:
                        raise_error("ARGUMENT ERROR: Trying to create a Rectangle object with points which X, Y coordinated are not num type.", token)    
                points.append(i.sol)

            elif type(i.sol) == dict:
                if "name" in i.sol.keys() and "x" in i.sol.keys() and "y" in i.sol.keys():
                    if i.sol["name"] == "Point":
                        points.append([i.sol["x"], i.sol["y"]])
                    else:
                        raise_error("ARGUMENT ERROR: name attribute should be Point", token)
                else:
                    raise_error("ARGUMENT ERROR: name,x,y attributes should be inside the Point attribute", token)
            else:
                raise_error("ARGUMENT ERROR: Trying to create a Rectangle object, wrong arguments, should be sets points (X,Y positions).", token)

        
        if len(args) != 4:
            raise_error("ARGUMENT ERROR: Number of points required to create a Rectangle is 4.", token)

        # Making the object's atributes

        # Sorting points so it always looks like a rectangle
        points = sorted(points, key=lambda p: (p[0], p[1]))

        # Ensure bottom-left and bottom-right are the first two points
        bottom_left, bottom_right = points[:2]

        # Ensure top-left and top-right are the last two points
        top_left, top_right = points[2:]

        # Reorder the points to avoid hourglass shape
        points = [bottom_left, bottom_right, top_right, top_left]

        # Sides
        sides = []
    
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]  # Connect to the next point, and wrap around
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            sides.append(distance)
        
        # Diagonal

        d1 = ((points[0][0] - points[2][0]) ** 2 + (points[0][1] - points[2][1]) ** 2) ** 0.5
        d2 = ((points[1][0] - points[3][0]) ** 2 + (points[1][1] - points[3][1]) ** 2) ** 0.5

        # Area
        area = sides[0]*sides[1]

        # Output

        return {
                "name":"Rectangle", 
                "points":points,
                "sides":sides,
                "area":area, 
                "perimeter":sum(sides),
                "diagonals":[d1, d2],
                }

    elif command == "Polyline":
        for i in args: 
            if type(i.sol) == list: 
                raise_error("ARGUMENT ERROR: Trying to create a Polyline object, wrong arguments, should be multiple sets that represent points (x,y)", token)
        if len(args) <= 1:
            raise_error("ARGUMENT ERROR: Number of points required to create a Line is at least 2.", token)
        
        obj = {"name":"Polyline",
               "points": [],
               "length": 0}
        for i,e in enumerate(args):
            if obj["points"] == []:
                x1, y1 = e.sol[0], e.sol[1]
                x2, y2 = e.sol[0], e.sol[1]
                c = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                obj["length"] = c
                obj["points"] = [[x1, y1]]
            else:
                x1, y1 = e.sol[0], e.sol[1]
                x2, y2 = obj["points"][-1]
                c = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                obj["length"] = obj["length"] + c
                obj["points"].append([x1, y1])

        return obj

    elif command == "Vector":
        if len(args) == 2:
            for i in args:
                if type(i.sol) in [int, float]:
                    ...
                else:
                    raise_error("ARGUMENT ERROR: Wrong argument type", token)
        x1, y1 = args[0].sol, args[1].sol
        a = x1
        b = y1
        obj = {"name": "Vector",
               "length":math.sqrt(a**2+b**2),
               "start": (0,0),
               "end": (x1, y1),
               "points":[[0,0], [x1,y1]]}
        return obj

    elif command == "InCircle":
        if len(args) == 1:
            if type(args[0].sol) != dict:
                raise_error("ARGUMENT ERROR: Trying to create an InCircle object with wrong arguments, should be a object.", token)
        else:
            raise_error("ARGUMENT ERROR: Trying to create an InCircle object with wrong arguments, should be a object.", token)
        if len(args[0].sol["points"]) == 3:
            points=args[0].sol["points"]
            #check for error
            for i in points:
                if type(i) != list or len(i) != 2 or type(i[0]) != int or type(i[1]) != int:
                    raise_error("ARGUMENT ERROR: points attribute is not in right format.", token)
            x1, y1 = points[0]
            x2, y2 = points[1]
            x3, y3 = points[2]

            a = ((x2 - x3) ** 2 + (y2 - y3) ** 2) ** 0.5
            b = ((x1 - x3) ** 2 + (y1 - y3) ** 2) ** 0.5
            c = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            incenter_x = (a * x1 + b * x2 + c * x3) / (a + b + c)
            incenter_y = (a * y1 + b * y2 + c * y3) / (a + b + c)
            incenter_point = [incenter_x, incenter_y]
            s = sum(args[0].sol["sides"]) / 2

            area = math.sqrt(s * (s - args[0].sol["sides"][0]) * (s - args[0].sol["sides"][1]) * (s - args[0].sol["sides"][2]))

            radius = area / s

            objc = {"name":"Circle",
                    "center":incenter_point,
                    "radius":radius,
                    "diameter": radius*2,
                    "perimeter": radius*2*math.pi,
                    "area": radius**2*math.pi}

            return objc
        
    elif command == "CircumCircle":
        if len(args) == 1:
            if type(args[0].sol) != dict:
                raise_error("ARGUMENT ERROR: Trying to create an Circle object with wrong arguments, should be a object.", token)
        else:
            raise_error("ARGUMENT ERROR: Trying to create an Circle object with wrong arguments, should be a object.", token)
        if len(args[0].sol["points"]) == 3:
            points=args[0].sol["points"]
            #check for error
            for i in points:
                if type(i) != list or len(i) != 2 or type(i[0]) != int or type(i[1]) != int:
                    raise_error("ARGUMENT ERROR: points attribute is not in right format.", token)
            
            x1, y1 = points[0]
            x2, y2 = points[1]
            x3, y3 = points[2]

            # Calculate midpoints of two sides
            mid_x1 = (x1 + x2) / 2
            mid_y1 = (y1 + y2) / 2
            mid_x2 = (x2 + x3) / 2
            mid_y2 = (y2 + y3) / 2

            # Slopes of the sides
            slope_1 = (y2 - y1) / (x2 - x1) if x2 != x1 else None
            slope_2 = (y3 - y2) / (x3 - x2) if x3 != x2 else None

            # Perpendicular slopes (negative reciprocal)
            if slope_1 is None:  # If vertical, perpendicular is horizontal (slope = 0)
                perp_slope_1 = 0
            elif slope_1 == 0:  # If horizontal, perpendicular is vertical (None)
                perp_slope_1 = None
            else:
                perp_slope_1 = -1 / slope_1

            if slope_2 is None:  # If vertical, perpendicular is horizontal
                perp_slope_2 = 0
            elif slope_2 == 0:  # If horizontal, perpendicular is vertical
                perp_slope_2 = None
            else:
                perp_slope_2 = -1 / slope_2

            # Solve for circumcenter (intersection of perpendicular bisectors)
            if perp_slope_1 is None:  # First bisector is vertical
                cx = mid_x1
                cy = perp_slope_2 * (cx - mid_x2) + mid_y2
            elif perp_slope_2 is None:  # Second bisector is vertical
                cx = mid_x2
                cy = perp_slope_1 * (cx - mid_x1) + mid_y1
            elif perp_slope_1 == 0:  # First bisector is horizontal
                cy = mid_y1
                cx = (cy - mid_y2) / perp_slope_2 + mid_x2
            elif perp_slope_2 == 0:  # Second bisector is horizontal
                cy = mid_y2
                cx = (cy - mid_y1) / perp_slope_1 + mid_x1
            else:
                # Solve y = mx + b for both bisectors
                b1 = mid_y1 - perp_slope_1 * mid_x1
                b2 = mid_y2 - perp_slope_2 * mid_x2
                cx = (b2 - b1) / (perp_slope_1 - perp_slope_2)
                cy = perp_slope_1 * cx + b1

            circumcenter = [cx, cy]

            # Find radius (distance from circumcenter to any point)
            radius = math.sqrt((cx - x1) ** 2 + (cy - y1) ** 2)

            # Create circle object
            objc = {"name":"Circle",
                    "center":circumcenter,
                    "radius":radius,
                    "diameter": radius*2,
                    "perimeter": radius*2*math.pi,
                    "area": radius**2*math.pi}

            return objc

    elif command == "get":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")
        if type(args[0].sol) == dict and type(args[1].sol) == str:
            if args[1].sol in args[0].sol:
                return args[0].sol[args[1].sol]
            else:
                raise_error("ARGUMENT ERROR: Trying to get nonexistent attribute.", token)
        else:
            raise_error("ARGUMENT ERROR: Wrong type declaration while trying to get specific attribute from a object.", token)
    
    elif command == "attr":
        if len(args) != 3:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")
        if type(args[0].sol) == dict and type(args[1].sol) == str:
            obj = args[0].sol
            var = args[0].dsc
            obj[args[1].sol] = args[2].sol
            if var in VARS:
                VARS[var] = obj
            else:
                raise_error("")
        else:
            raise_error("ARGUMENT ERROR: Wrong type declaration while trying to set specific attribute to a object.", token)
    # Operators
    elif command == "+":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == list and type(args[1].sol) == list:
            return args[0].sol+args[1].sol
        
        elif type(args[0].sol) == str and type(args[1].sol) == str:
            return (args[0].sol) + (args[1].sol)
        
        elif type(args[0].sol)==int and type(args[1].sol)==int:
            return int(args[0].sol) + int(args[1].sol)
        
        elif type(args[0].sol)==float and type(args[1].sol)==float:
            return float(args[0].sol) + float(args[1].sol)
        
        elif type(args[0].sol)==int and type(args[1].sol)==float:
            return float(args[0].sol) + float(args[1].sol)
        
        elif type(args[0].sol)==float and type(args[1].sol)==int:
            return float(args[0].sol) + float(args[1].sol)
        else:
            raise_error("ARGUMENT ERROR: Trying to add (+) two values with different or wrong type.", token)
            
    elif command == "*":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if is_int(args[0].sol) and is_int(args[1].sol):
            return int(args[0].sol) * int(args[1].sol)
        else:
            raise_error("ARGUMENT ERORR: Trying to multiply(*) two values with wrong type.", token)
    
    elif command == "/":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if is_int(args[0].sol) and is_int(args[1].sol):
            return int(args[0].sol) // int(args[1].sol)
        else:
            raise_error("ARGUMENT ERORR: Trying to multiply(*) two values with wrong type.", token)
            
    elif command == "-":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if is_int(args[0].sol) and is_int(args[1].sol):
            return int(args[0].sol) - int(args[1].sol)
        else:
            raise_error("ARGUMENT ERORR: Trying to substract(-) two values with wrong type.", token)

    elif command == ">":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == int and type(args[1].sol) == int:
            return args[0].sol > args[1].sol
        else:
            raise_error("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM", token)

    elif command == ">=":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == int and type(args[1].sol) == int:
            return args[0].sol >= args[1].sol
        else:
            raise_error("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM", token)

    elif command == "<":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == int and type(args[1].sol) == int:
            return args[0].sol < args[1].sol
        else:
            raise_error("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM", token)

    elif command == "<=":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == int and type(args[1].sol) == int:
            return args[0].sol <= args[1].sol
        else:
            raise_error("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM", token)

    elif command == "=":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")
            
        if type(args[0].sol) == int and type(args[1].sol) == int:
            return args[0].sol == args[1].sol
        elif type(args[0].sol) == str and type(args[1].sol) == str:
            return args[0].sol == args[1].sol
        else:
            raise_error("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM", token)

    elif command == "!=":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == int and type(args[1].sol) == int:
            return args[0].sol != args[1].sol
        else:
            raise_error("ARGUMENT ERROR: Trying to compare two values with wrong type, should be NUM", token)

    elif command == "not":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.")

        if type(args[0].sol) == bool:
            return not(args[0].sol)
        else:
            raise_error("ARGUMENT ERROR: Trying to do a NOT operation on a non bool value.", token)
    
    elif command == "and":
        if len(args) == 2:        
            if type(args[0].sol) == bool and type(args[1].sol) == bool:
                if args[0].sol == args[1].sol == True:
                    return True
                return False
            else:
                raise_error("ARGUMENT ERROR: Trying to do a AND operation on a non bool values.", token)
        else:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
    
    elif command == "or":
        if len(args) < 2:  # Provjerava da ima barem dva argumenta
            raise_error("ARGUMENT ERROR: Not enough arguments.", token)
        
        argsol = []
        for i in args:
            if i.typ != "BLN":
                raise_error("ARGUMENT ERROR: Trying to do an OR operation on a non-boolean value.", token)
            argsol.append(str(i.sol))  # Pretvaramo u string za evaluaciju
        
        evalstr = " or ".join(argsol)  # Spaja sve argumente OR operatorom
        return eval(evalstr)  # Evaluira izraz i vraća rezultat


    elif command == "xor":
        if len(args) < 2:
            raise_error("ARGUMENT ERROR: Not enough arguments.", token)
        argsol = []
        for i in args:
            if i.typ != "BLN":
                raise_error("ARGUMENT ERROR: Trying to do a XOR operation on a non-boolean value.", token)
            argsol.append(i.sol)  # Ovdje koristimo bool direktno, ne string

        result = sum(argsol) % 2 == 1  # XOR provjerava neparan broj TRUE vrijednosti
        return result
    
    # Loops Ifs Elifs Whiles
    
    elif command == "if":
        if len(args) not in  [2,3]:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == bool:
            if args[0].sol == True:
                if args[1].typ == "BLK":
                    args[1].evaluate(forced=True)
                else:
                    raise_error("ARGUMENT ERROR: Trying to run IF's THEN code, but it is not a BLK.", token)
            else:
                if len(args) == 3: # if there is an else block
                    if args[2].typ == "BLK":
                        args[2].evaluate(forced=True)
                    else:
                        raise_error("ARGUMENT ERROR: Trying to run ELSE's THEN code, but it is not a BLK.", token)
        else:
            raise_error("ARGUMENT ERROR: Condition is non bool type", token)
    
    elif command == "loop":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if args[1].typ != "BLK":
            raise_error("ARGUMENT ERROR: Trying to run a non BLK type argument in a loop", token)
        if type(args[0].sol) == int:
            for i in range(args[0].sol):
                args[1].evaluate(forced=True)
        else:
            raise_error("ARGUMENT ERROR: Trying to use non NUM value for FOR loop.", token)

    elif command == "for":
        if len(args) != 3:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if args[2].typ != "BLK":
            raise_error("ARGUMENT ERROR: Trying to run a non BLK type argument in a loop", token)
        if type(args[0].sol) == str:
            if type(args[1].sol) == list:
                if args[0] not in VARS:
                    VARS[args[0].sol] = 0
                    for i in (args[1].sol):
                        VARS[args[0].sol] = i
                        args[2].evaluate(forced=True)
                    VARS.pop(args[0].sol)
                else:
                    raise_error("ARGUMENT ERROR: Trying to set an index's name to a variable that has already been set.", token)
            else:
                raise_error("ARGUMENT ERROR: Trying to go trough non SET type in for command.", token)
        else:
            raise_error("ARGUMENT ERROR: Trying to set an index variable to a non TXT name", token)
    
    elif command == "random":
        if len(args) == 2:
            start = args[0].sol
            end = args[1].sol
            if type(start) == type(end) == int:
                return random.randint(start, end)
            else:
                raise_error("ARGUMENT ERROR: Lowest and the highest values need to be NUM type.")
        else:
            raise_error("ARGUMENT ERROR: random command only takes in 2 NUM types that represent lowest and the highest value command can result.", token)
    
    elif command == "seq":
        for a in args:
            if type(a.sol) != int:
                raise_error("ARGUMENT ERROR: All arguments in command seq should be NUM type.")
        if len(args) == 1:
            return list(range(args[0].sol))
        elif len(args) == 2:
            return list(range(args[0].sol, args[1].sol))
        elif len(args) == 3:
            return(list(range(args[0].sol, args[1].sol, args[2].sol)))
        else:
            raise_error("ARGUMENT ERROR: Number of arguments should be either 1,2 or 3")

    elif command == "while":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Number of arguments should be 2")
        if args[1].typ == "BLK" and type(args[0].sol) == bool:
            while args[0].sol:
                args[1].evaluate(forced=True)
                args[0].evaluate()
        else:
            raise_error("ARGUMENT ERROR: Trying to execute a argument that does not have the ability to be intepreted.", token)
            
    # Other commands

    elif command == "output":
        out = ""
        for arg in args:
            if arg.typ == "BLK":
                raise_error("ARGUMENT ERROR: output command can't take in block of code as an argument")

            elif type(arg.sol) == bool:
                out += (str(arg.sol).upper())
            else:
                out += str(arg.sol)
            out += " "
        
        print(out)
    
    elif command == "filter":

        if len(args) != 3:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        ret = []
        if len(args[2].arg) != 1:
            raise_error("ARGUMENT ERROR: Condiditon should be only one, in other words only one condition inside the parenthesis", token)

        if args[2].arg[0].typ != "COM":
            raise_error("ARGUMENT ERROR: Last argument in filter command needs to be condition with value TRUE or FALSE", token)
        
        if type(args[0].sol) == str and type(args[1].sol) == list and args[2].typ == "BLK":

            VARS[args[0].sol] = 0
            for i in args[1].sol:
                VARS[args[0].sol] = i
                tok = []
                cond = tokenize(args[2].dsc, tok)
                cond.evaluate()
                if type(cond.sol) != bool:
                    raise_error("ARGUMENT ERROR: Last argument in filter command needs to be condition with value TRUE or FALSE", token)
                if cond.sol:
                    ret.append(i)
            VARS.pop(args[0].sol)
                
            return ret
        else:
            raise_error("ARGUMENT ERROR: filter command should have first argument TXT, second SET and last one BLK type", token)


    elif command == "fetch":
        if len(args) == 2:
            if type(args[0].sol) == list and type(args[1].sol) == int:
                set_ = args[0].sol
                i_ = int(args[1].sol)
                try:
                    return set_[i_]
                except:
                    raise_error(f"INDEX ERROR: Trying to FETCH inexistent value at {i_} position in {set_} SET.", token)
            elif type(args[0].sol) == str and type(args[1].sol) == int:
                string = args[0].sol
                i_ = int(args[1].sol)
                try:
                    return string[i_]
                except:
                    raise_error(f"INDEX ERROR: Trying to FETCH inexistent value at {i_} position in {set_} TXT.", token)
            else:
                raise_error("ARGUMENT ERROR: Wrong type arguments for command fetch.")
                
        elif len(args) == 3:
            if type(args[0].sol) == list and type(args[1].sol) == int and type(args[2].sol) == int:
                set_ = args[0].sol
                i_ = args[1].sol
                j_ = args[2].sol
                try:
                    return set_[i_:j_]
                except:
                    raise_error(f"INDEX ERROR: trying to FETCH inexistent value from {i_} position to {j_} in {set_} SET.", token)

            elif type(args[0].sol) == list and type(args[1].sol) == int and type(args[2].sol) == int:
                string = args[0]
                i_ = args[1].sol
                j_ = args[2].sol
                try:
                    return string[i_:j_]
                except:
                    raise_error(f"INDEX ERROR: trying to FETCH inexistent value from {i_} position to {j_} in {set_} TXT.", token)
            
            else:
                raise_error("ARGUMENT ERROR: Wrong type arguments for command fetch.", token)
        
        else:
            raise_error("ARGUMENT ERROR: Number of arguments should be 2 or 3.", token)


    elif command == "remove":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Number of arguments should be 2", token)
        if type(args[0].sol) == list:
            if args[1].sol in args[0].sol:
                SET_UPDATED = args[0].sol
                SET_UPDATED.remove(args[1].sol)
                return SET_UPDATED
            else:
                raise_error("ARGUMENT ERROR: trying to remove an element that is not in SET", token)
        elif type(args[0].sol) == str:
            if args[1].sol in args[0].sol:
                SET_UPDATED = list(args[0].sol)
                for i in range(SET_UPDATED.count(args[1].sol)):
                    SET_UPDATED.remove(args[1].sol)
                return "".join(SET_UPDATED)
            else:
                raise_error("ARGUMENT ERROR: trying to remove an element into a wrong TYPE, should be SET", token)
        else:
            raise_error("ARGUMENT ERROR: trying to remove an element into a wrong TYPE, should be SET", token)
    
    elif command == "add":
        
        if type(args[0].sol) == list:
            if len(args) == 2:
                SET_UPDATED = args[0].sol
                SET_UPDATED.append(args[1].sol)
                return SET_UPDATED
            elif len(args) == 3:
                SET_UPDATED = args[0].sol
                try:
                    SET_UPDATED.insert(args[1].sol, args[2].sol)
                    return SET_UPDATED
                except:
                    raise_error("INDEX ERROR: Trying to insert value to a index thats not in SET")
            else:
                raise_error("ARGUMENT ERROR: Wrong number of arguments.")
        else:
            raise_error("ARGUMENT ERROR: trying to add an element into a wrong TYPE, should be SET", token)

    elif command == "union":
        union_set = []
        for a in args:
            if type(a.sol) == list:
                union_set += a.sol
            else:
                raise_error("ARGUMENT ERROR: trying to unionize elements that are wrong TYPE, both elements should be SET", token)
                
        union_set = list(set(union_set))
        return union_set
    
    elif command == "len":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == list or type(args[0].sol) == str:
            return len(args[0].sol)
        else:
            raise_error("ARGUMENT ERROR: Trying to get a length of a wrong type, should be SET or TXT.", token)
            

    elif command == "intersection":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        INTERSECTED = []
        if type(args[0].sol) == list and type(args[1].sol) == list:
            for E1 in args[0].sol:
                for E2 in args[1].sol:
                    if E1 == E2:
                        INTERSECTED.append(E1)
            return list(set(INTERSECTED))
        else:
            raise_error("ARGUMENT ERROR: trying to intersect elements that are wrong TYPE, both elements should be SET", token)

    elif command == "reverse":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == list:
            return args[0].sol[::-1]
        else:
            raise_error("ARGUMENT ERROR: reverse command can only be executed on SET type variables.")
        
    elif command == "sort":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if len(args) == 2:
            if type(args[1].sol) == str and args[1].sol.lower() == "<" and type(args[0].sol) == list:
                return sorted(args[0].sol)
            elif type(args[1].sol) == str and args[1].sol.lower() == ">" and type(args[0].sol) == list:
                return sorted(args[0].sol)[::-1]
            
            else:
                raise_error('ARGUMENT ERROR: sort command can only be executed on SET type values, second value can be TXT type, use "<" to sort it from smallest to highest and ">" for opposite.')
        else:
            if type(args[0].sol) == list:
                return sorted(args[0].sol)
            else:
                raise_error("ARGUMENT ERROR: sort command can only be executed on SET type values.", token)
            
    elif command == "subset":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == list and type(args[1].sol) == list:
            #QUICK CHECK
            if len(args[0].sol) > len(args[1].sol):
                return False
            
            strS1 = "".join(str(x) for x in args[0].sol)
            strS2 = "".join(str(x) for x in args[1].sol)  
            if strS1 in strS2: return True
        else:
            raise_error("ARGUMENT ERROR: trying to detect subsets of elements that are wrong TYPE, both elements should be SET", token)
            
        return False
    
    elif command == "superset":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == list and type(args[1].sol) == list:
            #QUICK CHECK
            if len(args[1].sol) > len(args[0].sol):
                return False
            
            strS1 = "".join(str(x) for x in args[0].sol)
            strS2 = "".join(str(x) for x in args[1].sol)  
            if strS2 in strS1: 
                return True
            
        else:
            raise_error("ARGUMENT ERROR: trying to detect subsets of elements that are wrong TYPE, both elements should be SET", token)
            
        return False
    
    elif command == "sum":
        if len(args) == 1:
            if type(args[0].sol) == list:
                return sum(args[0].sol)
            else:
                raise_error("ARGUMENT/TYPE ERROR: Trying to get a SUM of only one value or values are incorrect type.", token)
                
        else:
            sum_list = []
            for i in args:
                if i.typ == "NUM":
                    sum_list.append(i.sol)
                else:
                    raise_error("TYPE ERROR: Trying to get a SUM of multiple non NUM type values.", token)
                    
            return sum(sum_list)
        
    elif command == "max":
        if len(args) == 1:
            if type(args[0].sol) == list:
                return max(args[0].sol)
            else:
                raise_error("ARGUMENT/TYPE ERROR: Trying to get a MAX value of only one value, or values are incorrect type.", token)
                
        else:
            max_list = []
            for i in args:
                if i.typ == "NUM":
                    max_list.append(i.sol)
                else:
                    raise_error("TYPE ERROR: Trying to get a MAX value of mutlitple non NUM type values.", token)
                    
            return max(max_list)
        
    elif command == "min":
        if len(args) == 1:
            if type(args[0].sol) == list:
                return min(args[0].sol)
            else:
                raise_error("ARGUMENT/TYPE ERROR: Trying to get a MIN of only one value or values are incorrect type.", token)
                
        else:
            min_list = []
            for i in args:
                if i.typ == "NUM":
                    min_list.append(i.sol)
                else:
                    raise_error("TYPE ERROR: Trying to get a MIN value of mutlitple non NUM type values.", token)
                    
            return min(min_list)
    
    elif command == "disjunction":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == list and type(args[1].sol) == list:
            
            a = repeating_el(args[0].sol + args[1].sol)
            return a
            
        else:
            raise_error("ARGUMENT ERROR: trying to disjunct of elements that are wrong TYPE, both elements should be SET", token)
            
        return False

    elif command == "input":
        if len(args) > 1:
            raise_error("ARGUMENT ERROR: Input command only takes in one of the following arguments: txt, num, bln", token)
        a = input()
        type_conversion = args[0].sol
        if type_conversion.lower() == "num":
            if is_int(a):
                return int(a)
            else:
                raise_error("TYPE ERROR: Error while handling conversion from this argument's type to NUM type", token)
                
        elif type_conversion.lower() == "txt":
            return a

        elif type_conversion.lower() == "bln":

            if a in [0, "0"]:
                return False
            else:
                return True
        
        else:
            raise_error("ARGUMENT ERROR: Input's arguments should only be 'num', 'txt' or 'bln' depending on what type does a user wants to convert value into.", token)

    elif command == "var":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)

        if type(args[1].sol) in [int, str, bool, list, dict, float]:
            if args[0].sol not in BOOLS and args[0].sol != "pi":

                VARS[args[0].sol] = args[1].sol

            else:
                raise_error("ARGUMENT ERROR: Trying to set a variable's name to TRUE or FALSE, which can't be used as variables names.", token)
                                
        else:
            raise_error("ARGUMENT ERROR: Trying to set variable's value to incorrect type.", token)
            
        #return True
    
    elif command == "func":
        if len(args) != 2:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == str and (args[1].typ) == "BLK":
            FUNS[args[0].sol] = args[1]
        #return True

    elif command == "call":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if args[0].sol in FUNS:
            FUNS[args[0].sol].evaluate(forced=True)
        else:
            raise_error("ARGUMENT ERROR: Trying to run a nononexisent function.", token)
        #return True
    
    # Type conversions:
        
    elif command == "num":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if is_int(args[0].sol):
            return int(args[0].sol)
        else:
            raise_error("TYPE ERROR: Error while handling conversion from this argument's type to NUM type", token)
            

    elif command == "txt":
        if type(args[0].sol)==int or type(args[0].sol)==bool or type(args[0].sol)==float:
            if type(args[0].sol )== bool:
                return str(args[0].sol).upper()
            return str(args[0].sol)
        else:
            if type(args[0].sol) != str:
                raise_error("TYPE ERROR: Trying to convert non-convertable value into TXT type.", token)
                
            return str(args[0].sol)
    
    elif command == "upper":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == str:
            return args[0].sol.upper()
        else:
            raise_error(f"ARGUMENT ERROR: Wrong type declaration while trying to capitalize {args[0].typ} value, should be TXT", token)

    elif command == "lower":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == str:
            return args[0].sol.lower()
        else:
            raise_error(f"ARGUMENT ERROR: Wrong type declaration while trying to decapitalize {args[0].typ} value, should be TXT", token)
    
    elif command == "trim":
        if len(args) != 1:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)
        if type(args[0].sol) == str:
            v = args[0].sol
            return v.strip()
        else:
            raise_error("ARGUMENT ERROR: Trying to trim a non TXT value.")
    
    elif command == "replace":
        if len(args) != 3:
            raise_error("ARGUMENT ERROR: Wrong number of arguments.", token)

        if type(args[0].sol) == str and type(args[1].sol) == str and type(args[2].sol) == str:
            
            value = args[0].sol
            replaces = args[1].sol
            replacement = args[2].sol
            return value.replace(replaces, replacement)
        else:
            raise_error("ARGUMENT ERROR: Can't replace values that are not TXT type.")
        
    elif command == "set":
        lst = []
        if len(args) == 1 and args[0].sol == "_":
            return lst
        for a in args:
            lst.append(a.sol)
        return lst
    
    elif command == "setify":
        lst = []
        if len(args) == 1 and args[0].sol == "_":
            return lst
        if type(args[0].sol) == str:
            return list(args[0].sol)
        else:
            raise_error("ARGUMENT ERROR: setify command takes in only TXT arguments, _ for emtpy SET")
    
    #COMMAND NOT FOUND SYNTAX ERROR
    elif command not in COMMANDS:
        raise_error(f"SYNTAX ERROR: {command} is not a command or a variable.", token)
        
def tokenize(code, tokens_list=None):

    if DEVELOPER_MODE:
        print(f'DEBUG: - tokenizing: {code}')

    first_bracket = None
    last_bracket = None
    str_depth = False
    codeError = ""
    for i,e in enumerate(code):
        
        i1 = len(code) - i - 1

        if e == '"':
            str_depth = not(str_depth)
        
        if e == "(" and first_bracket is None and not(str_depth):
            first_bracket = i
            
        if code[i1] == ")" and last_bracket is None and not(str_depth):
            last_bracket = i1
        
        if not(str_depth):
            codeError += e
            
    # FIX CHECKING FOR ERROR IN BRACKET

    if codeError.count("(")!=codeError.count(")"):
        print(code)
        raise_error('SYNTAX ERROR: brackets are not balanced')
    
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

    if command and abs(first_bracket-last_bracket) == 1: #error for 0 arguments
        raise_error(f"ARGUMENT ERROR: Insuficient arguments in command '{command}' , every command is required to have arguments.")

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
    global VARS, FIDE_PATH, FILE_PATH
  
    FILE_PATH = file_path

    file = open(file_path)
    file_content = file.read()
    file.close()  #closing the file
    file_content = '(' + file_content + ')'
    
    # Removing " " in file
    n_catcher = 0
    i_spaces = []
    for i,f in enumerate(file_content):
        if  f == '"':
            n_catcher += 1
            if n_catcher == 2:
                n_catcher = 0

        if n_catcher==0 and f == " ":
            i_spaces.append(i)
    
    file_content = list(file_content)
    for i in i_spaces:
        file_content[i] = "~"
    file_content = "".join(file_content)
    file_content = file_content.replace("~", "")

    # Adding comments
    file_content = file_content.split("\n")
    for i,e in enumerate(file_content):
        if COMMENT in e:
            file_content[i] = e.split(COMMENT)[0]
    file_content = "".join(file_content)
    
    # Additional cleanup
    file_content = file_content.replace("\n", "")
    file_content = file_content.replace("\t", "")
    
    # Execute program
    TOKENS = []
    token_root = tokenize(file_content, TOKENS)
    token_root.evaluate(forced=True)
    return TOKENS, file_path

######
# MAIN
######

# Check if a .flow file is provided as an argument
#if not (len(sys.argv) == 2 or len(sys.argv) == 3 or len(sys.argv) == 4):
if len(sys.argv) < 2 or len(sys.argv) > 4:
    print(f"Usage: python FLOW.py <filename>.flow [flags]")
    sys.exit(1)

# Extract arguments
RUNNER = None
_, FILENAME, *flags = sys.argv
if "FIDE" in flags:
    RUNNER = "FIDE"
if "DEVELOPER_MODE" in flags:
    DEVELOPER_MODE = True

FILENAME = sys.argv[1]

VARS_CONNECTION_KEY = "[SENDING_VARS_TO_FIDE]"
FUNS_CONNECTION_KEY = "[SENDING_FUNS_TO_FIDE]"
INPUT_CONNECTION_KEY = "[RUNNING_IN_FIDE]"

# print(len(sys.argv))
TOKENS, _ = run(FILENAME)

# printing tokens
if DEVELOPER_MODE:
    print('DEBUG: List of created tokens:')
    for T in TOKENS:
        print(T)

# sending vars to FIDE
if RUNNER == "FIDE":
    print(VARS_CONNECTION_KEY+str(VARS))

    #formating FUNS
    formated_funs = []
    for i in FUNS:
        formated_funs.append(i)
    print(FUNS_CONNECTION_KEY+str(formated_funs))
