import rockets
import physics
import controllers
import visualization

# Runs the physics simulation only, without any graphical component. Then returns the state information necessary to reconstruct the physics simulation graphically.
# Each returned list contains the values of its corresponding attribute at every simulation timestep.
def simulate_physics(engine_names, controller=None):
    # Create the rocket physics simulator and add each engine defined in engine_names:
    rocket_simulator = rockets.Rocket(position_y=physics.INITIAL_ROCKET_HEIGHT)
    for engine_name in engine_names:
        rocket_simulator.add_engine(engine_name)
    # Keep track of all data that will be needed to visually reconstruct the rocket's trajectory:
    position_x_true, position_y_true, angular_position_true, angular_velocity_true = [], [], [], []
    engine_thrusts = []
    thrust_vectors = []
    fuel_masses = []
    altitude_sensor_readings, altitude_sensor_readings_scaled = [], []
    speed_sensor_readings, speed_sensor_readings_scaled = [], []
    angular_position_sensor_readings, angular_position_sensor_readings_scaled = [], []
    angular_velocity_sensor_readings, angular_velocity_sensor_readings_scaled = [], []
    # Runs the physics and graphics simulations:
    crashed = False
    fuel_empty = False
    while not crashed:
        # Make decisions on the control algorithm based on sensor readings and current thrust levels:
        rocket_simulator.control(controller)
        # Update the physics simulation
        thrust_vector = rocket_simulator.step()
        position_x_true.append(rocket_simulator.position_x)
        position_y_true.append(rocket_simulator.position_y)
        angular_position_true.append(rocket_simulator.angular_position)
        engine_thrusts.append([engine.current_thrust_ratio for engine in rocket_simulator.engines])
        thrust_vectors.append(thrust_vector)
        fuel_masses.append(rocket_simulator.fuel_mass / rocket_simulator.initial_fuel_mass)
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
        # Update global states (whether the rocket has crashed, whether it has run out of fuel):
        if not fuel_empty and rocket_simulator.fuel_mass <= 0:
            fuel_empty = True
            print("RAN OUT OF FUEL!")
        if rocket_simulator.position_y <= 0:
            crashed = True
    return (position_x_true, position_y_true, angular_position_true, angular_velocity_true), (altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings), (altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled), engine_thrusts, thrust_vectors, fuel_masses

# Runs the graphical simulation using an input Controller to make control decisions and using a rocket with the input engine names.
# The physics simulation is run first, and then the returned information is used to recreate the physics simulation in the graphical window.
def external_control(engine_names=["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"], controller=None, save=False):
    if controller is None:
        controller = controllers.Controller(n_engines=len(engine_names))
    # Run the physics simulation first: 
    (position_x_true, position_y_true, angular_position_true, angular_velocity_true), (altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings), (altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled), engine_thrusts, thrust_vectors, fuel_masses = simulate_physics(engine_names, controller)
    # Visualize the results graphically:
    simulation_data = {"position_x_true":position_x_true, "position_y_true":position_y_true, "angular_position_true":angular_position_true, "angular_velocity_true":angular_velocity_true, "altitude_sensor_readings":altitude_sensor_readings, "speed_sensor_readings":speed_sensor_readings, "angular_position_sensor_readings":angular_position_sensor_readings, "angular_velocity_sensor_readings":angular_velocity_sensor_readings, "altitude_sensor_readings_scaled":altitude_sensor_readings_scaled, "speed_sensor_readings_scaled":speed_sensor_readings_scaled, "angular_position_sensor_readings_scaled":angular_position_sensor_readings_scaled, "angular_velocity_sensor_readings_scaled":angular_velocity_sensor_readings_scaled, "engine_thrusts":engine_thrusts, "thrust_vectors":thrust_vectors, "fuel_masses":fuel_masses}
    visualization.visualize_simulation_from_data(simulation_data, engine_names=engine_names, save=save)