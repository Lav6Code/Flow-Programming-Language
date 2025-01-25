import turtle

def draw_grid(screen_width, screen_height, margin=50, step=50):
    t.penup()
    t.color("gray")
    
    # Draw vertical grid lines
    for x in range(-screen_width//2 + margin, screen_width//2, step):
        t.goto(x, screen_height//2 - margin)
        t.pendown()
        t.goto(x, -screen_height//2 + margin)
        t.penup()

    # Draw horizontal grid lines
    for y in range(-screen_height//2 + margin, screen_height//2, step):
        t.goto(screen_width//2 - margin, y)
        t.pendown()
        t.goto(-screen_width//2 + margin, y)
        t.penup()

    # Draw x and y axes
    t.color("black")
    t.goto(-screen_width//2, 0)
    t.pendown()
    t.goto(screen_width//2, 0)  # X axis
    t.penup()
    t.goto(0, -screen_height//2)
    t.pendown()
    t.goto(0, screen_height//2)  # Y axis

    # Label x and y axes
    t.penup()
    t.goto(screen_width//2 - 10, -10)
    t.write("X", font=("Arial", 12, "normal"))
    t.goto(10, screen_height//2 - 20)
    t.write("Y", font=("Arial", 12, "normal"))


# Function to scale points to fit the screen
def scale_points(points, screen_width, screen_height, margin=50):
    # If there is only one point, return the center position
    if len(points) == 1:
        return [(0,0)]
    
    min_x = min(x for x, y in points)
    max_x = max(x for x, y in points)
    min_y = min(y for x, y in points)
    max_y = max(y for x, y in points)

    # Calculate scaling factors
    point_width = max_x - min_x
    point_height = max_y - min_y
    scale_x = (screen_width - 2 * margin) / point_width if point_width > 0 else 1
    scale_y = (screen_height - 2 * margin) / point_height if point_height > 0 else 1
    
    # Use the smaller scale to maintain the aspect ratio
    scale = min(scale_x, scale_y)

    # Scale and center the points
    scaled_points = [
        ((x - min_x) * scale + margin - screen_width / 2, 
         (y - min_y) * scale + margin - screen_height / 2)
        for x, y in points
    ]
    return scaled_points

def scale_length(length, screen_width, screen_height, margin=50):
    # Assuming we want the length to fit within the available space on the screen
    available_width = screen_width - 2 * margin
    available_height = screen_height - 2 * margin
    
    # Calculate scaling factors based on both width and height
    scale_x = available_width / length if length > 0 else 1
    scale_y = available_height / length if length > 0 else 1
    
    # Use the smaller scale factor to maintain the aspect ratio (to prevent distortion)
    scale = min(scale_x, scale_y)
    
    # Return the scaled length
    return length * scale

def draw_polygon(points, screen_width, screen_height):
    scaled_points = scale_points(points, screen_width, screen_height)

    t.pensize(5)
    t.penup()
    t.goto(scaled_points[0])
    t.pendown()
    for x, y in scaled_points[1:]:
        t.goto(x, y)
    t.goto(scaled_points[0])

def draw_circle(object, screen_width, screen_height):

    scaled_points = scale_points([object["center"]], screen_width, screen_height)
    t.pensize(5)
    t.penup()
    diameter = scale_length(object["radius"], screen_width, screen_height)
    radius = diameter/2
    center_x, center_y = scaled_points[0]
    t.goto(center_x, center_y-radius)
    t.pendown()
    t.circle(radius)
    
def start(object):
    global t
    screen = turtle.Screen()
    screen.setup(width=600, height=600)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)

    screen.tracer(0)

    draw_grid(600, 600)
    print(object)
    if object["name"] == "Circle":
        draw_circle(object, 600, 600)
    else:
        points = object["points"]
        draw_polygon(points, 600, 600)

        

    screen.update()

    turtle.done()