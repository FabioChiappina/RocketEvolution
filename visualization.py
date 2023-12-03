import turtle
from turtle import Turtle, Screen
from PIL import Image, ImageGrab
import imageio
import time
from math import pi, cos, sin, atan2, sqrt
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import numpy as np
import os
import json

import physics
import rockets
import file_manager

# Creates and displays a visual of the simulation whose data is given by the input simulation_data dictionary.
# simulation_data dictionary should have the following fields:
# position_x_true, position_y_true, angular_position_true, angular_velocity_true, altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings, altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled, engine_thrusts, thrust_vectors, fuel_masses
def visualize_simulation_from_data(simulation_data, engine_names=["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"], show_details=False, save_path=None):
    position_x_true, position_y_true, angular_position_true, angular_velocity_true, altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings, altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled, engine_thrusts, thrust_vectors, fuel_masses = file_manager.unpack_simulation_data(simulation_data)

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
    engine_colors_dictionary = {"GreedyEngine":"dark orchid", "PatientEngine":"dark orange", "BullyEngine":"medium blue", "UpSteeringEngine":"dim gray", "DownSteeringEngine":"black"}
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
    if show_details:
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
    else:
        engine_summary = Turtle()
        engine_summary.hideturtle()
        engine_summary.up()
        engine_summary.goto(round(0.8*SCREEN_WIDTH),(0.8*SCREEN_HEIGHT))
        engine_summary.color('black')
        engine_summary.write(f'Range: {(0)}', align='left', font=('Courier', 34, 'bold'))

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
        if show_details:
            engine_summary.clear()
            engine_summary.write(f'Range: {round(rocket_graphic.xcor(),2)}\nGreedy Engine: {(round(float(engine_thrusts[iterator][engine_names.index("GreedyEngine")]),2) if "GreedyEngine" in engine_names else "---")}\nPatient Engine: {(round(float(engine_thrusts[iterator][engine_names.index("PatientEngine")]),2) if "PatientEngine" in engine_names else "---")}\nBully Engine: {(round(float(engine_thrusts[iterator][engine_names.index("BullyEngine")]),2) if "BullyEngine" in engine_names else "---")}\nUp-Steering Engine: {(round(float(engine_thrusts[iterator][engine_names.index("UpSteeringEngine")]),2) if "UpSteeringEngine" in engine_names else "---")}\nDown-Steering Engine: {(round(float(engine_thrusts[iterator][engine_names.index("DownSteeringEngine")]),2) if "DownSteeringEngine" in engine_names else "---")}', align='left', font=('Courier', 14, 'normal'))
            if iterator % 5 == 0:
                sensor_summary.clear()
                sensor_summary.write(f'Altitude Sensor: {round(altitude_sensor_readings[iterator],2)}\nSpeed Sensor: {round(speed_sensor_readings[iterator],2)}\nAngular Position Sensor: {round(angular_position_sensor_readings[iterator],2)}\nAngular Velocity Sensor: {round(angular_velocity_sensor_readings[iterator],2)}', align='left', font=('Courier', 14, 'normal'))
        else:
            if iterator % 2 == 0:
                engine_summary.clear()
                engine_summary.write(f'Range: {round(rocket_graphic.xcor(),2)}', align='left', font=('Courier', 34, 'bold'))
        # Update global states (whether the rocket has crashed, whether it has run out of fuel):
        if rocket_graphic.ycor() <= 0:
            crashed = True
            time.sleep(2)
        iterator += 1
        # Update the saving mp4 file:
        if save_path is not None:
            pass
    # Create an animation showing simulation statistics
    if save_path is not None:
        create_simulation_animation(simulation_data, engine_names, save_path)

# Loads simulation data stored in a json file and displays that simulated data in an animation.
def visualize_simulation_from_filename(simulation_data_filename, engine_names=["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"], show_details=False, save_path=None):
    if not (simulation_data_filename.endswith("run_data.json")):
        simulation_data_filename = os.path.join(simulation_data_filename, "run_data.json")
    if not (simulation_data_filename.endswith(".json")) and "." not in os.path.basename(simulation_data_filename):
        simulation_data_filename += ".json"
    with open(simulation_data_filename, 'r') as json_file:
        simulation_data = json.load(json_file)
    visualize_simulation_from_data(simulation_data, engine_names, show_details, save_path)

# Loads simulation data from an input individual within an input generation and with the specified run name.
def visualize_simulation_run(generation, individual, run_name=None, engines=None, results_path="Results", show_details=False, save=True):
    simulation_data, _, engine_names, individual_save_path = file_manager.load_run(generation, individual, run_name, engines, results_path)
    visualize_simulation_from_data(simulation_data, engine_names, show_details, None if ((not save) or save is None) else individual_save_path)

# Creates an animation of all sensor readings, fuel mass, and engine thrusts over the simulation time.
def create_simulation_animation(simulation_data, engine_names, save_path):
    position_x_true, _, _, _, _, _, _, _, altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled, engine_thrusts, _, fuel_masses = file_manager.unpack_simulation_data(simulation_data)
    times = np.arange(len(position_x_true)) * physics.TIMESTEP
    def animation_update_wrapper(axes, times, sensor_readings_list, sensor_titles_list, sensor_x_labels_list, sensor_y_labels_list, fuel_masses, engine_thrusts):
        update_sensor_subplots = [sensor_update_subplot_wrapper(axes[i], times, sensor_readings_list[i], sensor_titles_list[i], sensor_x_labels_list[i], sensor_y_labels_list[i]) for i in range(len(sensor_readings_list))]
        fuel_subplot = fuel_update_wrapper(axes[4], times, fuel_masses)
        engine_thrusts_subplot = engine_thrusts_wrapper(axes[5], engine_thrusts)
        def sensor_update(frame):
            for sensor_subplot in update_sensor_subplots:
                sensor_subplot(frame)
            fuel_subplot(frame)
            engine_thrusts_subplot(frame)
        return sensor_update
    def sensor_update_subplot_wrapper(ax, x, y, title, x_label, y_label):
        def sensor_update_subplot(frame):
            ax.clear()
            ax.scatter(x[:frame], y[:frame], s=1.0, c='green', marker='o')
            ax.set_xlim(0, max(x))
            ax.set_ylim(0, 1)
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
        return sensor_update_subplot
    def fuel_update_wrapper(ax, x, y, title="Remaining Fuel (% Of Max)", x_label="", y_label=""):
        def fuel_update(frame):
            ax.clear()
            ax.scatter(x[:frame], y[:frame], s=2.0, c='red', marker='o')
            ax.set_xlim(0, max(x))
            ax.set_ylim(0, 100)
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
        return fuel_update
    def engine_thrusts_wrapper(ax, engine_thrusts, engine_names=engine_names, title="Engine Thrusts (% Of Max)", x_label="Time (s)", y_label=""):
        def engine_update(frame):
            ax.clear()
            ax.bar([name[0].upper() for name in engine_names], engine_thrusts[frame], color=['purple', 'orange', 'blue', (0.5,0.5,0.5), 'black'][:len(engine_thrusts[frame])])
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_ylim(0, 100)
        return engine_update

    fig, axes = plt.subplots(2, 3, figsize=(17, 6.5))
    sensor_readings = [
        (altitude_sensor_readings_scaled, "Altitude Sensor Readings (0-1 Scaled)", "", ""),
        (speed_sensor_readings_scaled, "Speed Sensor Readings (0-1 Scaled)", "", ""),
        (angular_position_sensor_readings_scaled, "Angular Position Sensor Readings (0-1 Scaled)", "Time (s)", ""),
        (angular_velocity_sensor_readings_scaled, "Angular Velocity Sensor Readings (0-1 Scaled)", "Time (s)", "")
    ]
    axes = [axes[0,0], axes[0,1], axes[1,0], axes[1,1], axes[0,2], axes[1,2]]
    sensor_readings_list = [var[0] for var in sensor_readings]
    sensor_titles_list = [var[1] for var in sensor_readings]
    sensor_x_labels_list = [var[2] for var in sensor_readings]
    sensor_y_labels_list = [var[3] for var in sensor_readings]
    data_animation = animation.FuncAnimation(fig, animation_update_wrapper(axes, times, sensor_readings_list, sensor_titles_list, sensor_x_labels_list, sensor_y_labels_list, 100*np.array(fuel_masses), 100*np.array(engine_thrusts)), frames=len(times), interval=1, repeat=False)
    data_animation.save(os.path.join(save_path,'visualization.mp4'), writer=animation.FFMpegWriter(fps=60, codec="libx264", extra_args=["-pix_fmt", "yuv420p"]))
