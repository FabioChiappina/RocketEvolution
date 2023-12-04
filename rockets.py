import physics
from math import sin, cos, pi, log
import numpy as np

SCALER_ALTITUDE_SENSOR = 500 # m
SCALER_SPEED_SENSOR = 225 # m/s
SCALER_ANGULAR_POSITION_SENSOR = 2*pi # radians
SCALER_ANGULAR_VELOCITY_SENSOR = 3*pi # radians/s

class Engine:
    DEFAULT_NAME="Engine"
    DEFAULT_MASS=100
    DEFAULT_MAXIMUM_THRUST=100
    DEFAULT_TIME_TO_MAX_THRUST=1
    DEFAULT_EFFICIENCY=1
    DEFAULT_ANGLE_VARIANCE=1
    DEFAULT_POSITION_ON_FUSELAGE=0 # X-distance from rear-end of rocket, as a ratio of 0-1 (0=rear end, 1=front end)
    MAX_THRUST_ANGLE_VARIANCE=1*pi/18000 # In radians, equivalent to 1/50 degrees
    def __init__(self, name=DEFAULT_NAME, mass=DEFAULT_MASS, maximum_thrust=DEFAULT_MAXIMUM_THRUST, time_to_max_thrust=DEFAULT_TIME_TO_MAX_THRUST, efficiency=DEFAULT_EFFICIENCY, angle_variance=DEFAULT_ANGLE_VARIANCE, position_on_fuselage=DEFAULT_POSITION_ON_FUSELAGE, thrusting=False, current_thrust_ratio=0, current_thrust_angle=0):
        self.name=name
        self.mass = mass
        self.maximum_thrust = maximum_thrust
        self.time_to_max_thrust = time_to_max_thrust
        self.efficiency = efficiency
        self.angle_variance = angle_variance
        self.position_on_fuselage = position_on_fuselage
        self.thrusting = thrusting
        self.current_thrust_ratio = current_thrust_ratio
        self.current_thrust_angle = current_thrust_angle
    
    # Sets the boolean thrusting parameter to true. 
    # Computes and returns the current thrusting force.
    def thrust(self):
        self.thrusting = True
        if self.current_thrust_ratio < 0:
            self.current_thrust_ratio = 0
        elif self.current_thrust_ratio > 1:
            self.current_thrust_ratio = 1
        return self.maximum_thrust * self.current_thrust_ratio
    
    # Sets the boolean thrusting parameter to false and the current thrusting ratio to 0.
    def kill(self):
        self.thrusting = False
        self.current_thrust_ratio = 0

    # Steps the engine forward in the physics simulation by one timestep.
    # The current thrusting ratio and the current thrust angle are updated.
    # Returns the mass of fuel that the engine burns in that timestep.
    def step(self):
        if not self.thrusting:
            return
        if self.current_thrust_ratio <= 1:
            self.current_thrust_ratio += physics.TIMESTEP / self.time_to_max_thrust
            self.current_thrust_ratio = min(self.current_thrust_ratio, 1)
        self.current_thrust_angle += np.random.normal(0, np.sqrt(self.angle_variance * Engine.MAX_THRUST_ANGLE_VARIANCE),1)[0]
    
    # Consumes fuel mass according to the current thrusting force.
    # Returns the mass of the fuel consumed.
    def consume_fuel(self):
        if not self.thrusting:
            return 0
        current_thrust = self.thrust()
        fuel_mass_consumed = current_thrust * physics.TIMESTEP / (physics.FUEL_FORCE_PER_UNIT_MASS_FLOW_RATE * self.efficiency)
        return fuel_mass_consumed
    
    # Returns the current thrusting force decomposed into its x and y components.
    # Note that these components are from the reference frame of the rocket, NOT from a global reference frame.
    def thrust_components(self):
        if not self.thrusting:
            return 0,0
        current_thrust = self.thrust()
        return current_thrust * cos(self.current_thrust_angle), current_thrust * sin(self.current_thrust_angle)

class GreedyEngine(Engine):
    name = "GreedyEngine"
    mass = 125
    maximum_thrust = 40000
    time_to_max_thrust = 1
    efficiency = 0.4
    angle_variance = 0.4
    position_on_fuselage = 0

    def __init__(self):
        super().__init__(__class__.name, __class__.mass, __class__.maximum_thrust, __class__.time_to_max_thrust, __class__.efficiency, __class__.angle_variance, __class__.position_on_fuselage)

class PatientEngine(Engine):
    name = "PatientEngine"
    mass = 250
    maximum_thrust = 65000
    time_to_max_thrust = 6
    efficiency = 0.99
    angle_variance = 0.15
    position_on_fuselage = 0

    def __init__(self):
        super().__init__(__class__.name, __class__.mass, __class__.maximum_thrust, __class__.time_to_max_thrust, __class__.efficiency, __class__.angle_variance, __class__.position_on_fuselage)

class BullyEngine(Engine):
    name = "BullyEngine"
    mass = 400
    maximum_thrust = 120000
    time_to_max_thrust = 3
    efficiency = 0.65
    angle_variance = 1
    position_on_fuselage = 0

    def __init__(self):
        super().__init__(__class__.name, __class__.mass, __class__.maximum_thrust, __class__.time_to_max_thrust, __class__.efficiency, __class__.angle_variance, __class__.position_on_fuselage)

class UpSteeringEngine(Engine):
    name = "UpSteeringEngine"
    mass = 80
    maximum_thrust = 12000
    time_to_max_thrust = 0.4
    efficiency = 0.9
    angle_variance = 0.1
    position_on_fuselage = 0.9

    def __init__(self):
        super().__init__(__class__.name, __class__.mass, __class__.maximum_thrust, __class__.time_to_max_thrust, __class__.efficiency, __class__.angle_variance, __class__.position_on_fuselage, current_thrust_angle=pi/4)

class DownSteeringEngine(Engine):
    name = "DownSteeringEngine"
    mass = 80
    maximum_thrust = 12000
    time_to_max_thrust = 0.4
    efficiency = 0.9
    angle_variance = 0.1
    position_on_fuselage = 0.9

    def __init__(self):
        super().__init__(__class__.name, __class__.mass, __class__.maximum_thrust, __class__.time_to_max_thrust, __class__.efficiency, __class__.angle_variance, __class__.position_on_fuselage, current_thrust_angle=-pi/4)

class Rocket:
    DEFAULT_FUSELAGE_LENGTH = 20 # m
    DEFAULT_FUSELAGE_MASS = 180 # Kg
    DEFAULT_FUEL_MASS = 2000 # Kg

    def __init__(self, fuselage_length=DEFAULT_FUSELAGE_LENGTH, fuselage_mass=DEFAULT_FUSELAGE_MASS, fuel_mass=DEFAULT_FUEL_MASS, position_x=0, position_y=0, velocity_x=0, velocity_y=0, angular_position=0, angular_velocity=0):
        self.fuselage_length = fuselage_length
        self.fuselage_mass = fuselage_mass
        self.fuel_mass = fuel_mass
        self.initial_fuel_mass = fuel_mass
        self.position_x = position_x
        self.position_y = position_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.angular_velocity = angular_velocity
        self.angular_position = angular_position
        self.engines = []

    def get_mass(self):
        return self.fuselage_mass + self.fuel_mass + sum(engine.mass for engine in self.engines)
    
    def get_center_of_mass(self):
        return (((self.fuselage_mass+self.fuel_mass) * 0.5) + sum([engine.position_on_fuselage * engine.mass for engine in self.engines])) * self.fuselage_length / self.get_mass()
    
    def get_moment_of_inertia(self):
        return (1/12 * (self.fuselage_mass+self.fuel_mass) * self.fuselage_length**2) + sum([engine.mass * (self.fuselage_length * engine.position_on_fuselage - self.get_center_of_mass())**2 for engine in self.engines])
    
    def true_speed(self):
        return np.sqrt(self.velocity_x**2 + self.velocity_y**2)
    
    def altitude_sensor(self, sigma=4):
        return self.position_y + np.random.normal(0, sigma, 1)[0]
    
    def speed_sensor(self, sigma=3):
        return self.true_speed() + np.random.normal(0, sigma, 1)[0]
    
    def angular_position_sensor(self, sigma=0.4):
        return self.angular_position + np.random.normal(0, sigma, 1)[0]
    
    def angular_velocity_sensor(self, sigma=0.5):
        return self.angular_velocity + np.random.normal(0, sigma, 1)[0]
    
    # Returns the altitude, speed, and angular position all scaled to a 0-1 range. Used in the control system.
    def sense(self):
        altitude = self.altitude_sensor()
        altitude = altitude / SCALER_ALTITUDE_SENSOR
        if altitude > 1:
            altitude = 1 + log(altitude) # Using this trick so that scaled altitude readings won't go far above 1, but can still be slightly greater than 1
        speed = self.speed_sensor()
        speed = speed / SCALER_SPEED_SENSOR
        if speed > 1:
            speed = 1 + log(speed) # Using this trick so that scaled speed readings won't go far above 1, but can still be slightly greater than 1
        angular_position = self.angular_position_sensor()
        angular_position = ((angular_position-pi) % (2*pi)) / SCALER_ANGULAR_POSITION_SENSOR
        # Mapped 0 radians to 0.5 in feature space, since this is likely the most common angle, so we don't want to be constantly swapping between 0/1 here.
        # -pi radians maps to 0 in feature space. pi radians maps to 1 in feature space.
        angular_velocity = self.angular_velocity_sensor()
        angular_velocity = (angular_velocity + SCALER_ANGULAR_VELOCITY_SENSOR) / (2*SCALER_ANGULAR_VELOCITY_SENSOR)
        # Mapped 0 rad/s to 0.5 in feature space, with negative angular velocities approaching 0 and positive approaching 1
        return altitude, speed, angular_position, angular_velocity
    
    def add_engine(self, engine):
        if isinstance(engine, Engine):
            self.engines.append(engine)
        elif type(engine)==str:
            engine = engine.lower()
            if engine == "greedyengine":
                self.engines.append(GreedyEngine())
            elif engine == "patientengine":
                self.engines.append(PatientEngine())
            elif engine == "bullyengine":
                self.engines.append(BullyEngine())
            elif engine == "upsteeringengine":
                self.engines.append(UpSteeringEngine())
            elif engine == "downsteeringengine":
                self.engines.append(DownSteeringEngine())
            else:
                print(f"Engine type '{engine}' is not recognized and was not added.")
        else:
            print("Input engine must be an instance of Engine or must be a string.")

    # Updates the physics simulated parameters of the Rocket, including the mass of fuel it has remaining, its position, velocity, angular position, and angular velocity, etc.
    # Returns the thrust vector in the global reference frame.
    def step(self):
        fuel_mass_consumed = 0
        thrust_x_rocket_reference_frame = 0
        thrust_y_rocket_reference_frame = 0
        torque = 0
        if any([isinstance(engine, BullyEngine) and engine.thrusting for engine in self.engines]): # Implementing the Bully behavior -- if the Bully engine is on, it turns all other engines off.
            for engine in self.engines:
                if not isinstance(engine, BullyEngine):
                    engine.kill()
        for engine in self.engines:
            engine.step()
            this_fuel_mass_consumed = engine.consume_fuel()
            thrust_x, thrust_y = engine.thrust_components()
            cm = self.get_center_of_mass()
            if fuel_mass_consumed + this_fuel_mass_consumed <= self.fuel_mass:
                thrust_x_rocket_reference_frame += thrust_x
                thrust_y_rocket_reference_frame += thrust_y
                torque += (engine.position_on_fuselage * self.fuselage_length - cm) * thrust_y
                fuel_mass_consumed += this_fuel_mass_consumed
            elif fuel_mass_consumed <= self.fuel_mass:
                thrust_x_rocket_reference_frame += thrust_x * ((self.fuel_mass - fuel_mass_consumed)/this_fuel_mass_consumed)
                thrust_y_rocket_reference_frame += thrust_y * ((self.fuel_mass - fuel_mass_consumed)/this_fuel_mass_consumed)
                torque += (engine.position_on_fuselage * self.fuselage_length - cm) * thrust_y * ((self.fuel_mass - fuel_mass_consumed)/this_fuel_mass_consumed)
                fuel_mass_consumed = self.fuel_mass
        thrust_x_global_reference_frame = thrust_x_rocket_reference_frame * cos(self.angular_position) - thrust_y_rocket_reference_frame * sin(self.angular_position)
        thrust_y_global_reference_frame = thrust_x_rocket_reference_frame * sin(self.angular_position) + thrust_y_rocket_reference_frame * cos(self.angular_position)
        acceleration_x = thrust_x_global_reference_frame / self.get_mass()
        acceleration_y = thrust_y_global_reference_frame / self.get_mass() - physics.GRAVITY
        self.position_x += self.velocity_x * physics.TIMESTEP + 0.5 * acceleration_x * physics.TIMESTEP**2
        self.position_y += self.velocity_y * physics.TIMESTEP + 0.5 * acceleration_y * physics.TIMESTEP**2
        self.velocity_x += acceleration_x * physics.TIMESTEP
        self.velocity_y += acceleration_y * physics.TIMESTEP
        angular_acceleration = torque / self.get_moment_of_inertia()
        self.angular_position += self.angular_velocity * physics.TIMESTEP + 0.5 * angular_acceleration * physics.TIMESTEP**2
        self.angular_velocity += angular_acceleration * physics.TIMESTEP
        self.fuel_mass = max(0, self.fuel_mass - fuel_mass_consumed)
        if self.fuel_mass == 0:
            [engine.kill() for engine in self.engines]
        if self.position_y <= 0:
            self.position_y = 0
            self.velocity_x = 0
            self.velocity_y = 0
            print("\nCRASHED! ---------------------------------\n\tRange:", self.position_x, "\n\tRemaining fuel mass:", self.fuel_mass, "("+str(round(self.fuel_mass/self.initial_fuel_mass*100,2))+"%)")
        return [thrust_x_global_reference_frame, thrust_y_global_reference_frame]

    def control(self, controller=None):
        sensor_readings = list(self.sense())
        engine_thrusts = [engine.current_thrust_ratio for engine in self.engines]
        fuel_mass = self.fuel_mass / self.initial_fuel_mass
        if controller is None:
            return
        prediction = controller.predict(sensor_readings, engine_thrusts, fuel_mass)
        for i, this_engine_prediction in enumerate([p for p in prediction[0]]):
            if this_engine_prediction < 0.5:
                self.engines[i].kill()
            else:
                self.engines[i].thrust()