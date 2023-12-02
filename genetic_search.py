import keras_genetic
import external_control
import controllers
import os
import json

# TODO -- now that I'm returning fuel and thrust percentages, should make cool animated graphs for thrust amounts per engine and for fuel amount. Could be a single animated subplot 3x2 (4 ssensors, one engine thrusts, one fuel)

POPULATION_SIZE = 1 # TODO -- increase
GENERATIONS = 1     # TODO -- increase
GENERATION_COUNTER = 0
INDIVIDUAL_COUNTER = 1

# Define a custom evaluator function. (Horizontal rocket range.)
def controller_fitness_wrapper(engine_names, controller, save_path=None):
    def controller_fitness(individual: keras_genetic.Individual):
        controller.model = individual.load_model()
        # Count which individual in which generation is running:
        global INDIVIDUAL_COUNTER, GENERATION_COUNTER
        print("Running individual", INDIVIDUAL_COUNTER, "in generation", GENERATION_COUNTER)
        if INDIVIDUAL_COUNTER >= POPULATION_SIZE:
            INDIVIDUAL_COUNTER = 1
            GENERATION_COUNTER += 1
        else:
            INDIVIDUAL_COUNTER += 1
        # Run the physics simulation: 
        (position_x_true, position_y_true, angular_position_true, angular_velocity_true), (altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings), (altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled), engine_thrusts, thrust_vectors, fuel_masses = external_control.simulate_physics(engine_names, controller)
        # Save the data to the appropriate folder:
        if save_path is not None:
            data_dict = {
                "position_x_true": position_x_true,
                "position_y_true": position_y_true,
                "angular_position_true": angular_position_true,
                "angular_velocity_true": angular_velocity_true,
                "altitude_sensor_readings": altitude_sensor_readings,
                "speed_sensor_readings": speed_sensor_readings,
                "angular_position_sensor_readings": angular_position_sensor_readings,
                "angular_velocity_sensor_readings": angular_velocity_sensor_readings,
                "altitude_sensor_readings_scaled": altitude_sensor_readings_scaled,
                "speed_sensor_readings_scaled": speed_sensor_readings_scaled,
                "angular_position_sensor_readings_scaled": angular_position_sensor_readings_scaled,
                "angular_velocity_sensor_readings_scaled": angular_velocity_sensor_readings_scaled,
                "engine_thrusts": engine_thrusts,
                "thrust_vectors": thrust_vectors,
                "fuel_masses": fuel_masses
            }
            with open(os.path.join(save_path, "run_data.json"), "w") as json_file:
                json.dump(data_dict, json_file)
        return position_x_true[-1]
    return controller_fitness

# Perform the genetic algorithm to find "good" model weights
def search(engine_names, controller, generations=100, population_size=50, n_parents_from_population=4, return_best=2, save_path=None):
    # Configure the saving of results to the proper folder
    if save_path is not None:
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        if not ("run" in os.path.basename(save_path)):
            subfolders = os.listdir(save_path)
            last_run_number = 0
            for subfolder in subfolders:
                if "run" in subfolder and len(subfolder)>3:
                    try:
                        last_run_number = max(int(subfolder[3:]), last_run_number)
                    except:
                        pass
            run_name = "run" + "0"*(3-len(str(last_run_number+1))) + str(last_run_number+1)
            save_path = os.path.join(save_path, run_name)
            os.mkdir(save_path)
    # Run the evolutionary search
    results = keras_genetic.search(
        model=controller.model,
        evaluator=controller_fitness_wrapper(engine_names, controller, save_path),
        generations=generations,
        population_size=population_size,
        breeder=keras_genetic.breeder.MutationBreeder(),
        n_parents_from_population=n_parents_from_population,
        return_best=return_best,
    )
    model = results.best.load_model()
    controller = controllers.Controller(model=model)
    return model, controller

# Example:
engine_names = ["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"]
# Define the Controller algorithm that will decide when to turn on/off each engine.
controller = controllers.Controller(n_engines=len(engine_names))

model, controller = search(engine_names, controller, generations=GENERATIONS, population_size=POPULATION_SIZE, n_parents_from_population=2, save_path="Results")
external_control.external_control(engine_names, controller)