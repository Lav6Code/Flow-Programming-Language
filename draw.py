import turtle

def calculate_global_extent(objects):
    """Calculate the maximum extent of all objects to adjust the grid size."""
    if not isinstance(objects, list):
        objects = [objects]  # Convert single object to a list

    max_x, max_y = 0, 0
    for obj in objects:
        if obj["name"] == "Circle":
            center_x, center_y = obj["center"]
            radius = obj["radius"]
            max_x = max(max_x, center_x + radius)
            max_y = max(max_y, center_y + radius)
        elif obj["name"] in ["Triangle", "Polyline", "Line", "Rectangle"]:
            for x, y in obj["points"]:
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    return max_x+1, max_y+1

def draw_grid(screen_width, screen_height, max_x, max_y, margin=50):
    """Draws a grid in the first quadrant, scaled to fit all objects."""
    t.penup()
    t.color("gray")

    step = (screen_height - margin * 2) // (max(max_x, max_y) or 1)  # Avoid division by zero
    origin_x = -screen_width // 2 + margin
    origin_y = -screen_height // 2 + margin

    for y in range(1, max_y + 1):
        t.goto(origin_x, origin_y + (y - 1) * step)
        if y != 1:
            a = t.heading()
            t.setheading(180)
            t.forward(10)
            t.write(y-1)
            t.goto(origin_x, origin_y + (y - 1) * step)
            t.setheading(a)
        t.pendown()
        t.goto(origin_x + (max_x - 1) * step, origin_y + (y - 1) * step)
        t.penup()

    for x in range(1, max_x + 1):
        t.goto(origin_x + (x - 1) * step, origin_y)
        if x != 1:
            a = t.heading()
            t.setheading(270)
            t.forward(20)
            t.write(x-1)
            t.goto(origin_x + (x - 1) * step, origin_y)
            t.setheading(a)
        else:
            a = t.heading()
            t.setheading(270)
            t.forward(20)
            t.setheading(180)
            t.forward(10)
            t.write(0)
            t.goto(origin_x + (x - 1) * step, origin_y)
            t.setheading(a)
        t.pendown()
        t.goto(origin_x + (x - 1) * step, origin_y + (max_y - 1) * step)
        t.penup()

    t.color("black")
    t.pensize(3)
    t.goto(origin_x, origin_y)
    t.pendown()
    t.goto(origin_x + (max_x - 1) * step, origin_y)
    t.penup()
    t.goto(origin_x, origin_y)
    t.pendown()
    t.goto(origin_x, origin_y + (max_y - 1) * step)
    t.penup()
    t.goto(origin_x + (max_x - 1) * step + 10, origin_y - 10)
    t.write("X", font=("Arial", 12, "bold"))
    t.goto(origin_x - 20, origin_y + (max_y - 1) * step + 5)
    t.write("Y", font=("Arial", 12, "bold"))

def scale_points(points, screen_width, screen_height, max_x, max_y, margin=50):
    step = (screen_height - margin * 2) // (max(max_x, max_y) or 1)
    origin_x = -screen_width // 2 + margin
    origin_y = -screen_height // 2 + margin
    return [(origin_x + x * step, origin_y + y * step) for x, y in points]

def draw_polygon(points, screen_width, screen_height, max_x, max_y):
    scaled_points = scale_points(points, screen_width, screen_height, max_x, max_y)
    t.pensize(3)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    for x, y in scaled_points[1:]:
        t.goto(x, y)
    t.goto(scaled_points[0])

def draw_polyline(points, screen_width, screen_height, max_x, max_y):
    scaled_points = scale_points(points, screen_width, screen_height, max_x, max_y)
    t.pensize(3)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    for x, y in scaled_points:
        t.goto(x, y)

def draw_circle(circle_obj, screen_width, screen_height, max_x, max_y, margin=50):
    step = (screen_height - 2 * margin) // (max(max_x, max_y) or 1)
    scaled_center = scale_points([circle_obj["center"]], screen_width, screen_height, max_x, max_y)[0]
    scaled_radius = (circle_obj["radius"]) * step
    t.penup()
    t.goto(scaled_center[0], scaled_center[1] - scaled_radius)
    t.pendown()
    t.pensize(3)
    t.circle(scaled_radius)

def start(objects):

    global t
    screen_width = 600
    screen_height = 600
    margin = 50

    if not isinstance(objects, list):
        objects = [objects]

    max_x, max_y = calculate_global_extent(objects)
    max_x, max_y = round(max_x)+1, round(max_y)+1
    screen = turtle.Screen()
    screen.setup(width=screen_width, height=screen_height)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed()
    screen.tracer(0)
    draw_grid(screen_width, screen_height, max_x, max_y, margin)

    for obj in objects:
        if obj["name"] == "Circle":
            draw_circle(obj, screen_width, screen_height, max_x, max_y, margin)
        elif obj["name"] in ["Polyline", "Line"]:
            draw_polyline(obj["points"], screen_width, screen_height, max_x, max_y)
        elif obj["name"] in ["Triangle", "Rectangle"]:
            draw_polygon(obj["points"], screen_width, screen_height, max_x, max_y)

    screen.update()
    turtle.done()
