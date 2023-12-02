from turtle import Turtle, Screen
import time
from math import pi, cos, sin, atan2, sqrt
from matplotlib import pyplot as plt
import numpy as np
import rockets
import physics

# Initialization parameters:
SCREEN_WIDTH  = 1500 # m
SCREEN_HEIGHT = 400  # m
ROCKET_WIDTH_TO_LENGTH_RATIO = 0.2
BASE_TURTLE_SQUARE_WIDTH = 20

# Define the screen parameters for the simulation window:
screen = Screen()
screen.bgcolor('lightyellow')
screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
screen.setworldcoordinates(0, 0, screen.window_width(), screen.window_height())
screen.tracer(0)
screen.listen()

# Define the graphic turtle object used to display the rocket body in the simulation window:
rocket_graphic = Turtle()
rocket_graphic.shape('square')
rocket_graphic.shapesize(ROCKET_WIDTH_TO_LENGTH_RATIO,1)
rocket_graphic.color('dark green')
rocket_graphic.penup()
rocket_graphic.setpos(0, physics.INITIAL_ROCKET_HEIGHT)
rocket_graphic.pendown()

# Define a thrust vector turtle object used to visualize the direction of the rocket thrust, and a method for drawing an arrow in the graphics window.
thrust_graphic = Turtle()
thrust_graphic.hideturtle()
thrust_graphic.width(2)
def draw_arrow(arrow_turtle, length, angle_degrees, color="red"):
    arrow_turtle.color(color)
    arrow_turtle.pendown()
    arrow_turtle.setheading(angle_degrees)
    arrow_turtle.forward(length)
    arrow_turtle.penup()

# Define the names of the engines to be included in this simulation:
engine_names = ["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"]
engine_colors_dictionary = {"GreedyEngine":"indigo", "PatientEngine":"dim gray", "BullyEngine":"navy", "UpSteeringEngine":"black", "DownSteeringEngine":"black"}
engine_graphic_sizes_dictionary = {"GreedyEngine":0.25, "PatientEngine":0.325, "BullyEngine":0.4, "UpSteeringEngine":0.1, "DownSteeringEngine":0.1}
engine_graphics_offsets_dictionary = {"GreedyEngine":-0.3, "PatientEngine":-0.4, "BullyEngine":-0.6, "UpSteeringEngine":0.3, "DownSteeringEngine":0.3}
engine_graphics = []
for engine_name in engine_names:
    engine_graphic = Turtle()
    engine_graphic.shape('square')
    engine_graphic.shapesize(engine_graphic_sizes_dictionary[engine_name],engine_graphic_sizes_dictionary[engine_name])
    engine_graphic.color(engine_colors_dictionary[engine_name])
    engine_graphic.penup()
    engine_graphic.setpos(0, physics.INITIAL_ROCKET_HEIGHT)
    engine_graphics.append(engine_graphic)

# Create the rocket physics simulator and add each engine defined in engine_names:
rocket_simulator = rockets.Rocket(position_y=physics.INITIAL_ROCKET_HEIGHT)
for engine_name in engine_names:
    rocket_simulator.add_engine(engine_name)

# Given an input engine name, returns a function that, when called, turns on that engine if it's off, or turns it off if it's on:
def toggle_engine(engine_name):
    engine_name = engine_name.lower()
    index = -1
    for ei, engine in enumerate(rocket_simulator.engines):
        if engine.name.lower() == engine_name:
            index = ei
            break
    def toggle_engine_dummy():
        pass
    if index < 0:
        print("Engine name not found.")
        return toggle_engine_dummy
    def toggle_engine_helper():
        if rocket_simulator.engines[index].thrusting:
            rocket_simulator.engines[index].kill()
            print("KILLING ENGINE: ", rocket_simulator.engines[index].name)
        else:
            rocket_simulator.engines[index].thrust()
            print("STARTING ENGINE: ", rocket_simulator.engines[index].name)
        print("\t(detected key pressed: "+rocket_simulator.engines[index].name.lower()[0].upper()+")")
    return toggle_engine_helper

# Define the keyboard keys that need to be pressed to toggle on/off each of the following engines:
engine_key_dictionary = {"GreedyEngine": "g", "PatientEngine": "p", "BullyEngine": "b", "UpSteeringEngine": "u", "DownSteeringEngine": "d"}
for engine_name in engine_names:    
    screen.onkey(toggle_engine(engine_name), engine_key_dictionary[engine_name])

# Define an engine_summary turtle for displaying text in the simulation window on which engines are firing:
engine_summary = Turtle()
engine_summary.hideturtle()
engine_summary.up()
engine_summary.goto(round(0.8*SCREEN_WIDTH),50)
engine_summary.color('black')
engine_summary.write(f'Range: {0}\nGreedy Engine: {(int(rocket_simulator.engines[engine_names.index("GreedyEngine")].thrusting) if "GreedyEngine" in engine_names else "---")}\nPatient Engine: {(int(rocket_simulator.engines[engine_names.index("PatientEngine")].thrusting) if "PatientEngine" in engine_names else "---")}\nBully Engine: {(int(rocket_simulator.engines[engine_names.index("BullyEngine")].thrusting) if "BullyEngine" in engine_names else "---")}\nUp-Steering Engine: {(int(rocket_simulator.engines[engine_names.index("UpSteeringEngine")].thrusting) if "UpSteeringEngine" in engine_names else "---")}\nDown-Steering Engine: {(int(rocket_simulator.engines[engine_names.index("DownSteeringEngine")].thrusting) if "DownSteeringEngine" in engine_names else "---")}', align='left', font=('Courier', 14, 'normal'))
# Define a sensor_summary turtle for displaying text in the simulation window on the sensor readings:
sensor_summary = Turtle()
sensor_summary.hideturtle()
sensor_summary.up()
sensor_summary.goto(round(0.8*SCREEN_WIDTH),150)
sensor_summary.color('black')
sensor_summary.write(f'Altitude Sensor: {round(rocket_simulator.altitude_sensor(),2)}\nSpeed Sensor: {round(rocket_simulator.speed_sensor(),2)}\nAngular Position Sensor: {round(rocket_simulator.angular_position_sensor(),2)}\nAngular Velocity Sensor: {round(rocket_simulator.angular_velocity_sensor(),2)}', align='left', font=('Courier', 14, 'normal'))

# Runs the physics and graphics simulations:
altitude_sensor_readings, altitude_sensor_readings_scaled = [], []
speed_sensor_readings, speed_sensor_readings_scaled = [], []
angular_position_sensor_readings, angular_position_sensor_readings_scaled = [], []
angular_velocity_sensor_readings, angular_velocity_sensor_readings_scaled = [], []
crashed = False
fuel_empty = False
iterator = 0
while not crashed:
    screen.update()
    # Update the physics simulation
    thrust_vector = rocket_simulator.step()
    # Update the rocket body graphic position/orientation
    rocket_graphic.goto(rocket_simulator.position_x, rocket_simulator.position_y)
    rocket_graphic.setheading(rocket_simulator.angular_position * 180/pi)
    # Update the thrust vector graphic:
    thrust_graphic.clear()
    if not fuel_empty:
        thrust_graphic.goto(rocket_simulator.position_x, rocket_simulator.position_y)
        thrust_angle = atan2(thrust_vector[1], thrust_vector[0])
        thrust_length = sqrt(thrust_vector[0]**2 + thrust_vector[1]**2)
        if thrust_length > 0:
            thrust_graphic.showturtle()
        draw_arrow(thrust_graphic, 0.002*thrust_length, thrust_angle*180/pi + 180)
    # Update the engine body graphics positions/orientations
    for ei, engine_graphic in enumerate(engine_graphics):
        x_offset = engine_graphics_offsets_dictionary[engine_names[ei]]*BASE_TURTLE_SQUARE_WIDTH*cos(rocket_graphic.heading()*pi/180)
        y_offset = engine_graphics_offsets_dictionary[engine_names[ei]]*BASE_TURTLE_SQUARE_WIDTH*sin(rocket_graphic.heading()*pi/180)
        if engine_names[ei]=="UpSteeringEngine":
            x_offset += 0.15*BASE_TURTLE_SQUARE_WIDTH*sin(rocket_simulator.angular_position)
            y_offset += -0.15*BASE_TURTLE_SQUARE_WIDTH*cos(rocket_simulator.angular_position)
        elif engine_names[ei]=="DownSteeringEngine":
            x_offset += -0.15*BASE_TURTLE_SQUARE_WIDTH*sin(rocket_simulator.angular_position)
            y_offset += 0.15*BASE_TURTLE_SQUARE_WIDTH*cos(rocket_simulator.angular_position)            
        engine_graphic.goto(rocket_graphic.xcor()+x_offset, rocket_graphic.ycor()+y_offset)
        engine_graphic.setheading(rocket_graphic.heading())
    # Update sensor readings
    altitude, speed, angular_position, angular_velocity = rocket_simulator.altitude_sensor(), rocket_simulator.speed_sensor(), rocket_simulator.angular_position_sensor(), rocket_simulator.angular_velocity_sensor()
    scaled_altitude, scaled_speed, scaled_angular_position, scaled_angular_velocity = rocket_simulator.sense()
    altitude_sensor_readings.append(altitude)
    altitude_sensor_readings_scaled.append(scaled_altitude)
    speed_sensor_readings.append(speed)
    speed_sensor_readings_scaled.append(scaled_speed)
    angular_position_sensor_readings.append(angular_position)
    angular_position_sensor_readings_scaled.append(scaled_angular_position)
    angular_velocity_sensor_readings.append(angular_velocity)
    angular_velocity_sensor_readings_scaled.append(scaled_angular_velocity)
    # Update the text display
    engine_summary.clear()
    engine_summary.write(f'Range: {round(rocket_graphic.xcor(),2)}\nGreedy Engine: {(int(rocket_simulator.engines[engine_names.index("GreedyEngine")].thrusting) if "GreedyEngine" in engine_names else "---")}\nPatient Engine: {(int(rocket_simulator.engines[engine_names.index("PatientEngine")].thrusting) if "PatientEngine" in engine_names else "---")}\nBully Engine: {(int(rocket_simulator.engines[engine_names.index("BullyEngine")].thrusting) if "BullyEngine" in engine_names else "---")}\nUp-Steering Engine: {(int(rocket_simulator.engines[engine_names.index("UpSteeringEngine")].thrusting) if "UpSteeringEngine" in engine_names else "---")}\nDown-Steering Engine: {(int(rocket_simulator.engines[engine_names.index("DownSteeringEngine")].thrusting) if "DownSteeringEngine" in engine_names else "---")}', align='left', font=('Courier', 14, 'normal'))
    if iterator % 5 == 0:
        sensor_summary.clear()
        sensor_summary.write(f'Altitude Sensor: {round(altitude_sensor_readings[iterator],2)}\nSpeed Sensor: {round(speed_sensor_readings[iterator],2)}\nAngular Position Sensor: {round(angular_position_sensor_readings[iterator],2)}\nAngular Velocity Sensor: {round(angular_velocity_sensor_readings[iterator],2)}', align='left', font=('Courier', 14, 'normal'))
    # Update global states (whether the rocket has crashed, whether it has run out of fuel):
    if not fuel_empty and rocket_simulator.fuel_mass <= 0:
        fuel_empty = True
        thrust_graphic.hideturtle()
        print("RAN OUT OF FUEL!")
    if rocket_graphic.ycor() <= 0:
        crashed = True
        time.sleep(2)
    iterator += 1

plt.subplots(4,1)
plt.subplot(4,1,1)
plt.scatter(np.arange(len(altitude_sensor_readings)) * physics.TIMESTEP, altitude_sensor_readings, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Altitude (m)")
plt.subplot(4,1,2)
plt.scatter(np.arange(len(speed_sensor_readings)) * physics.TIMESTEP, speed_sensor_readings, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")
plt.subplot(4,1,3)
plt.scatter(np.arange(len(angular_position_sensor_readings)) * physics.TIMESTEP, angular_position_sensor_readings, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Angular Position (rad)")
plt.subplot(4,1,4)
plt.scatter(np.arange(len(angular_velocity_sensor_readings)) * physics.TIMESTEP, angular_velocity_sensor_readings, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Angular Velocity (rad/s)")
plt.show()

plt.subplots(4,1)
plt.subplot(4,1,1)
plt.scatter(np.arange(len(altitude_sensor_readings_scaled)) * physics.TIMESTEP, altitude_sensor_readings_scaled, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Altitude (Scaled)")
plt.subplot(4,1,2)
plt.scatter(np.arange(len(speed_sensor_readings_scaled)) * physics.TIMESTEP, speed_sensor_readings_scaled, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Speed (Scaled)")
plt.subplot(4,1,3)
plt.scatter(np.arange(len(angular_position_sensor_readings_scaled)) * physics.TIMESTEP, angular_position_sensor_readings_scaled, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Angular Position (Scaled)")
plt.subplot(4,1,4)
plt.scatter(np.arange(len(angular_velocity_sensor_readings_scaled)) * physics.TIMESTEP, angular_velocity_sensor_readings_scaled, s=1)
plt.xlabel("Time (s)")
plt.ylabel("Angular Velocity (Scaled)")
plt.show()