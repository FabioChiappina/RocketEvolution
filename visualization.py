from turtle import Turtle, Screen
import time
from math import pi, cos, sin, atan2, sqrt
from matplotlib import pyplot as plt
import numpy as np
import os
import json

import physics
import rockets
import file_manager

# Creates and displays a visual of the simulation whose data is given by the input simulation_data dictionary.
# simulation_data dictionary should have the following fields:
# position_x_true, position_y_true, angular_position_true, angular_velocity_true, altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings, altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled, engine_thrusts, thrust_vectors, fuel_masses
def visualize_simulation_from_data(simulation_data, engine_names=["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"], save=True):
    position_x_true = simulation_data["position_x_true"]
    position_y_true = simulation_data["position_y_true"]
    angular_position_true = simulation_data["angular_position_true"]
    angular_velocity_true = simulation_data["angular_velocity_true"]
    altitude_sensor_readings = simulation_data["altitude_sensor_readings"]
    speed_sensor_readings = simulation_data["speed_sensor_readings"]
    angular_position_sensor_readings = simulation_data["angular_position_sensor_readings"]
    angular_velocity_sensor_readings = simulation_data["angular_velocity_sensor_readings"]
    altitude_sensor_readings_scaled = simulation_data["altitude_sensor_readings_scaled"]
    speed_sensor_readings_scaled = simulation_data["speed_sensor_readings_scaled"]
    angular_position_sensor_readings_scaled = simulation_data["angular_position_sensor_readings_scaled"]
    angular_velocity_sensor_readings_scaled = simulation_data["angular_velocity_sensor_readings_scaled"]
    engine_thrusts = simulation_data["engine_thrusts"]
    thrust_vectors = simulation_data["thrust_vectors"]
    fuel_masses = simulation_data["fuel_masses"]

    # Initialization parameters:
    SCREEN_WIDTH  = 1700 # m
    SCREEN_HEIGHT = 450  # m
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

    # Define an engine_summary turtle for displaying text in the simulation window on which engines are firing:
    engine_summary = Turtle()
    engine_summary.hideturtle()
    engine_summary.up()
    engine_summary.goto(round(0.8*SCREEN_WIDTH),50)
    engine_summary.color('black')
    engine_summary.write(f'Range: {(0)}\nGreedy Engine: {(0 if "GreedyEngine" in engine_names else "---")}\nPatient Engine: {(0 if "PatientEngine" in engine_names else "---")}\nBully Engine: {(0 if "BullyEngine" in engine_names else "---")}\nUp-Steering Engine: {(0 if "UpSteeringEngine" in engine_names else "---")}\nDown-Steering Engine: {(0 if "DownSteeringEngine" in engine_names else "---")}', align='left', font=('Courier', 14, 'normal'))
    # Define a sensor_summary turtle for displaying text in the simulation window on the sensor readings:
    sensor_summary = Turtle()
    sensor_summary.hideturtle()
    sensor_summary.up()
    sensor_summary.goto(round(0.8*SCREEN_WIDTH),150)
    sensor_summary.color('black')
    sensor_summary.write(f'Altitude Sensor: {0}\nSpeed Sensor: {0}\nAngular Position Sensor: {round(0)}\nAngular Velocity Sensor: {round(0)}', align='left', font=('Courier', 14, 'normal'))

    # Using data obtained from the physics simulation, recreate that data in the graphics simulation:
    crashed = False
    iterator = 0
    while not crashed:
        screen.update()
        rocket_graphic.goto(position_x_true[iterator], position_y_true[iterator])
        rocket_graphic.setheading(angular_position_true[iterator] * 180/pi)
        # Update the thrust vector graphic:
        thrust_graphic.clear()
        if fuel_masses[iterator]==0:
            thrust_graphic.hideturtle()
        else:
            thrust_graphic.goto(position_x_true[iterator], position_y_true[iterator])
            thrust_angle = atan2(thrust_vectors[iterator][1], thrust_vectors[iterator][0])
            thrust_length = sqrt(thrust_vectors[iterator][0]**2 + thrust_vectors[iterator][1]**2)
            if thrust_length > 0:
                thrust_graphic.showturtle()
            draw_arrow(thrust_graphic, 0.002*thrust_length, thrust_angle*180/pi + 180)
        # Update the engine body graphics positions/orientations
        for ei, engine_graphic in enumerate(engine_graphics):
            x_offset = engine_graphics_offsets_dictionary[engine_names[ei]]*BASE_TURTLE_SQUARE_WIDTH*cos(rocket_graphic.heading()*pi/180)
            y_offset = engine_graphics_offsets_dictionary[engine_names[ei]]*BASE_TURTLE_SQUARE_WIDTH*sin(rocket_graphic.heading()*pi/180)
            if engine_names[ei]=="UpSteeringEngine":
                x_offset += 0.15*BASE_TURTLE_SQUARE_WIDTH*sin(angular_position_true[iterator])
                y_offset += -0.15*BASE_TURTLE_SQUARE_WIDTH*cos(angular_position_true[iterator])
            elif engine_names[ei]=="DownSteeringEngine":
                x_offset += -0.15*BASE_TURTLE_SQUARE_WIDTH*sin(angular_position_true[iterator])
                y_offset += 0.15*BASE_TURTLE_SQUARE_WIDTH*cos(angular_position_true[iterator])    
            engine_graphic.goto(rocket_graphic.xcor()+x_offset, rocket_graphic.ycor()+y_offset)
            engine_graphic.setheading(rocket_graphic.heading())
        # Update the text display
        engine_summary.clear()
        engine_summary.write(f'Range: {round(rocket_graphic.xcor(),2)}\nGreedy Engine: {(round(float(engine_thrusts[iterator][engine_names.index("GreedyEngine")]),2) if "GreedyEngine" in engine_names else "---")}\nPatient Engine: {(round(float(engine_thrusts[iterator][engine_names.index("PatientEngine")]),2) if "PatientEngine" in engine_names else "---")}\nBully Engine: {(round(float(engine_thrusts[iterator][engine_names.index("BullyEngine")]),2) if "BullyEngine" in engine_names else "---")}\nUp-Steering Engine: {(round(float(engine_thrusts[iterator][engine_names.index("UpSteeringEngine")]),2) if "UpSteeringEngine" in engine_names else "---")}\nDown-Steering Engine: {(round(float(engine_thrusts[iterator][engine_names.index("DownSteeringEngine")]),2) if "DownSteeringEngine" in engine_names else "---")}', align='left', font=('Courier', 14, 'normal'))
        if iterator % 5 == 0:
            sensor_summary.clear()
            sensor_summary.write(f'Altitude Sensor: {round(altitude_sensor_readings[iterator],2)}\nSpeed Sensor: {round(speed_sensor_readings[iterator],2)}\nAngular Position Sensor: {round(angular_position_sensor_readings[iterator],2)}\nAngular Velocity Sensor: {round(angular_velocity_sensor_readings[iterator],2)}', align='left', font=('Courier', 14, 'normal'))
        # Update global states (whether the rocket has crashed, whether it has run out of fuel):
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

# Loads simulation data stored in a json file and displays that simulated data in an animation.
def visualize_simulation_from_filename(simulation_data_filename, engine_names=["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"], save=False):
    if not (simulation_data_filename.endswith("run_data.json")):
        simulation_data_filename = os.path.join(simulation_data_filename, "run_data.json")
    if not (simulation_data_filename.endswith(".json")) and "." not in os.path.basename(simulation_data_filename):
        simulation_data_filename += ".json"
    with open(simulation_data_filename, 'r') as json_file:
        simulation_data = json.load(json_file)
    visualize_simulation_from_data(simulation_data, engine_names, save)

# Loads simulation data from an input individual within an input generation and with the specified run name.
def visualize_simulation_run(generation, individual, run_name=None, engines=None, results_path="Results", save=False):
    simulation_data, _, engine_names = file_manager.load_run(generation, individual, run_name, engines, results_path)
    visualize_simulation_from_data(simulation_data, engine_names, save)