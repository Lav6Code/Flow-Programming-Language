import turtle
import math

def calculate_global_extent(objects):
    """Calculate the maximum extent of all objects to adjust the grid size."""
    max_x, max_y = 0, 0
    for obj in objects:
        if obj["name"] == "Circle":
            center_x, center_y = obj["center"]
            radius = obj["radius"]
            max_x = max(max_x, abs(center_x) + radius)
            max_y = max(max_y, abs(center_y) + radius)
        elif obj["name"] in ["Graph", "Triangle", "Polyline", "Line", "Rectangle"]:
            for x, y in obj["points"]:
                max_x = max(max_x, abs(x))
                max_y = max(max_y, abs(y))
    return max_x + 1, max_y + 1

def draw_grid(screen_width, screen_height, max_x, max_y, margin=50):
    """Draws a grid centered at (0,0), covering all four quadrants."""
    t.penup()
    t.color("gray")
    step = (screen_height - margin * 2) // (2 * max(max_x, max_y) or 1)
    
    # Draw horizontal lines
    for y in range(-max_y, max_y + 1):
        t.goto(-max_x * step, y * step)
        t.pendown()
        t.goto(max_x * step, y * step)
        t.penup()
        if y != 0:
            t.goto(5, y * step - 5)
            t.write(y, align="left", font=("Arial", 10, "normal"))
    
    # Draw vertical lines
    for x in range(-max_x, max_x + 1):
        t.goto(x * step, -max_y * step)
        t.pendown()
        t.goto(x * step, max_y * step)
        t.penup()
        if x != 0:
            t.goto(x * step + 5, -15)
            t.write(x, align="center", font=("Arial", 10, "normal"))
    
    # Draw axes with arrows
    t.color("black")
    t.pensize(3)
    
    # X-axis
    t.goto(-max_x * step, 0)
    t.pendown()
    t.goto(max_x * step, 0)
    t.penup()
    t.goto(max_x * step - 10, -5)
    t.pendown()
    t.goto(max_x * step, 0)
    t.goto(max_x * step - 10, 5)
    t.penup()
    
    # Y-axis
    t.goto(0, -max_y * step)
    t.pendown()
    t.goto(0, max_y * step)
    t.penup()
    t.goto(-5, max_y * step - 10)
    t.pendown()
    t.goto(0, max_y * step)
    t.goto(5, max_y * step - 10)
    t.penup()
    
    # Label axes
    t.goto(max_x * step - 20, -25)
    t.write("X", font=("Arial", 12, "bold"))
    t.goto(-25, max_y * step - 20)
    t.write("Y", font=("Arial", 12, "bold"))

def scale_points(points, screen_width, screen_height, max_x, max_y, margin=50):
    """Scale points to fit within the centered grid."""
    step = (screen_height - margin * 2) // (2 * max(max_x, max_y) or 1)
    return [(x * step, y * step) for x, y in points]

def draw_polyline(points):
    scaled_points = scale_points(points, screen_width, screen_height, max_x, max_y)
    t.pensize(3)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    for x, y in scaled_points:
        t.goto(x, y)

def draw_polygon(points):
    scaled_points = scale_points(points, screen_width, screen_height, max_x, max_y)
    t.pensize(3)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    for x, y in scaled_points[1:]:
        t.goto(x, y)
    t.goto(scaled_points[0])

def draw_circle(circle_obj):
    step = (screen_height - 2 * margin) // (2 * max(max_x, max_y) or 1)
    scaled_center = scale_points([circle_obj["center"]], screen_width, screen_height, max_x, max_y)[0]
    scaled_radius = circle_obj["radius"] * step
    t.penup()
    t.goto(scaled_center[0], scaled_center[1] - scaled_radius)
    t.pendown()
    t.pensize(3)
    t.circle(scaled_radius)

def draw_graph(graph_obj, screen_width, screen_height, max_x, max_y):
    """Draw a graph based on the slope and intercept in the object."""
    slope = graph_obj['slope']
    intercept = graph_obj['intercept']
    
    # Define the range for x values
    x_start, x_end = -max_x, max_x  # Set to max_x for full range
    
    # Initialize list to hold points
    points = []
    
    # Calculate the points to plot based on the slope-intercept form
    for x in range(x_start, x_end + 1):
        y_value = slope * x + intercept  # y = mx + b
        points.append((x, y_value))
    
    # Scale points to fit in the drawing area
    scaled_points = scale_points(points, screen_width, screen_height, max_x, max_y)
    
    t.pensize(3)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    
    # Draw the line
    for x, y in scaled_points[1:]:
        t.goto(x, y)

    # Logic to label the function
    mid_x = (scaled_points[0][0] + scaled_points[-1][0]) / 2
    mid_y = (scaled_points[0][1] + scaled_points[-1][1]) / 2
    
    t.penup()
    t.goto(mid_x, mid_y)
    t.write(f'y={slope}x+{intercept}', align="center", font=("Arial", 12, "normal"))

def start(objects):
    global t, screen_width, screen_height, max_x, max_y, margin
    
    screen_width, screen_height = 600, 600
    margin = 50
    
    if not isinstance(objects, list):
        objects = [objects]
    
    max_x, max_y = calculate_global_extent(objects)
    max_x, max_y = round(max_x) + 1, round(max_y) + 1
    max_x = max(max_x, max_y)
    max_y = max_x
    
    screen = turtle.Screen()
    screen.setup(width=screen_width, height=screen_height)
    
    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    screen.tracer(0)
    draw_grid(screen_width, screen_height, max_x, max_y, margin)
    
    for obj in objects:
        if obj["name"] == "Circle":
            draw_circle(obj)
        elif obj["name"] in ["Polyline", "Line"]:
            draw_polyline(obj["points"])
        elif obj["name"] in ["Triangle", "Rectangle"]:
            draw_polygon(obj["points"])
        elif obj["name"] == "Graph":
            draw_graph(obj, screen_width, screen_height, max_x, max_y)
    
    screen.update()
    turtle.done()
