import turtle

def calculate_global_extent(objects):
    """Calculate the maximum extent of all objects to adjust the grid size."""
    max_x, max_y = 0, 0
    for obj in objects:
        if obj["name"] == "Circle":
            center_x, center_y = obj["center"]
            radius = obj["radius"]
            max_x = max(max_x, center_x + radius)
            max_y = max(max_y, center_y + radius)
        elif obj["name"] == "Polygon":
            for x, y in obj["points"]:
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    return max_x, max_y


def draw_grid(screen_width, screen_height, max_x, max_y, margin=50):
    """Draws a grid in the first quadrant, scaled to fit all objects."""
    t.penup()
    t.color("gray")

    step = (screen_height - margin * 2) // (max(max_x, max_y) - 1)  # Adjust for grid size
    origin_x = -screen_width // 2 + margin
    origin_y = -screen_height // 2 + margin

    # Draw horizontal lines
    for y in range(1, max_y + 1):  # Start from 1 instead of 0
        t.goto(origin_x, origin_y + (y - 1) * step)
        t.pendown()
        t.goto(origin_x + (max_x - 1) * step, origin_y + (y - 1) * step)
        t.penup()

    # Draw vertical lines
    for x in range(1, max_x + 1):  # Start from 1 instead of 0
        t.goto(origin_x + (x - 1) * step, origin_y)
        t.pendown()
        t.goto(origin_x + (x - 1) * step, origin_y + (max_y - 1) * step)
        t.penup()

    t.color("black")
    t.pensize(3)

    # X-axis
    t.goto(origin_x, origin_y)
    t.pendown()
    t.goto(origin_x + (max_x - 1) * step, origin_y)
    t.penup()

    # Y-axis
    t.goto(origin_x, origin_y)
    t.pendown()
    t.goto(origin_x, origin_y + (max_y - 1) * step)
    t.penup()

    # Labels
    t.goto(origin_x + (max_x - 1) * step + 10, origin_y - 10)
    t.write("X", font=("Arial", 12, "bold"))
    t.goto(origin_x - 15, origin_y + (max_y - 1) * step + 5)
    t.write("Y", font=("Arial", 12, "bold"))


def scale_points(points, screen_width, screen_height, max_x, max_y, margin=50):
    """Scales and shifts points to fit the grid."""
    step = (screen_height - margin * 2) // (max(max_x, max_y) - 1)
    origin_x = -screen_width // 2 + margin
    origin_y = -screen_height // 2 + margin

    return [(origin_x + (x - 1) * step, origin_y + (y - 1) * step) for x, y in points]


def draw_polygon(points, screen_width, screen_height, max_x, max_y):
    """Draws a polygon after scaling it properly."""
    scaled_points = scale_points(points, screen_width, screen_height, max_x, max_y)

    t.pensize(3)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    for x, y in scaled_points[1:]:
        t.goto(x, y)
    t.goto(scaled_points[0])


def draw_circle(circle_obj, screen_width, screen_height, max_x, max_y, margin=50):
    """Draws a circle with radius equal to one grid square."""
    step = (screen_height - 2 * margin) // (max(max_x, max_y) - 1)

    scaled_center = scale_points([circle_obj["center"]], screen_width, screen_height, max_x, max_y)[0]
    scaled_radius = circle_obj["radius"] * step  # Scale radius to grid

    t.penup()
    t.goto(scaled_center[0], scaled_center[1] - scaled_radius)  # Move to bottom of circle
    t.pendown()
    t.pensize(3)
    t.circle(scaled_radius)


def start(objects):
    """Initializes Turtle and draws all objects."""
    global t
    screen_width = 600
    screen_height = 600
    margin = 50

    # Calculate global grid extent
    max_x, max_y = calculate_global_extent(objects)

    screen = turtle.Screen()
    screen.setup(width=screen_width, height=screen_height)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)

    screen.tracer(0)

    # Draw grid
    draw_grid(screen_width, screen_height, max_x, max_y, margin)

    # Draw each object
    for obj in objects:
        if obj["name"] == "Circle":
            draw_circle(obj, screen_width, screen_height, max_x, max_y, margin)
        elif obj["name"] in  ["Triangle"]:
            draw_polygon(obj["points"], screen_width, screen_height, max_x, max_y)

    screen.update()
    turtle.done()
