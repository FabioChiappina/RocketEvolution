import keras_genetic
import os
import json
import numpy as np

import external_control
import controllers
import file_manager


POPULATION_SIZE = 30 
GENERATIONS = 250     

GENERATION_COUNTER = 0
INDIVIDUAL_COUNTER = 0

run_name = None # None if you want to start a new run. Otherwise, give the string name of the run to pick up where a previous run left off (NOTE -- this only somewhat works)
engine_names = ["PatientEngine", "UpSteeringEngine", "DownSteeringEngine"] # NOTE: removed bully engine and greedy engine

# Define the Controller algorithm that will decide when to turn on/off each engine.
if run_name is None:
    controller = controllers.Controller(n_engines=len(engine_names))
else:
    run_path = os.path.join("Results", run_name)
    if not os.path.exists(run_path):
        raise ValueError("Input run name not found.")
    generation_paths = [generation for generation in os.listdir(run_path) if "store" not in generation.lower()]
    last_generation_path = os.path.join(run_path, sorted(generation_paths)[-1])
    GENERATION_COUNTER += int(os.path.basename(last_generation_path)) + 1
    individual_paths = [individual for individual in os.listdir(last_generation_path) if "store" not in individual.lower()]
    individual_path = os.path.join(last_generation_path, sorted(individual_paths)[-1])
    controller = controllers.Controller.load(individual_path)

# Define a custom evaluator function. (Horizontal rocket range.)
def controller_fitness_wrapper(engine_names, controller, run_save_path):
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
        n_repeats = 3 # How many times the fitness simulation should be re-run for a single individual's fitness. The median fitness value is what is kept.
        fitnesses = []
        position_x_true_list, position_y_true_list, angular_position_true_list, angular_velocity_true_list, altitude_sensor_readings_list, speed_sensor_readings_list, angular_position_sensor_readings_list, angular_velocity_sensor_readings_list, altitude_sensor_readings_scaled_list, speed_sensor_readings_scaled_list, angular_position_sensor_readings_scaled_list, angular_velocity_sensor_readings_scaled_list, engine_thrusts_list, thrust_vectors_list, fuel_masses_list = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
        for nr in range(n_repeats):
            (position_x_true, position_y_true, angular_position_true, angular_velocity_true), (altitude_sensor_readings, speed_sensor_readings, angular_position_sensor_readings, angular_velocity_sensor_readings), (altitude_sensor_readings_scaled, speed_sensor_readings_scaled, angular_position_sensor_readings_scaled, angular_velocity_sensor_readings_scaled), engine_thrusts, thrust_vectors, fuel_masses = external_control.simulate_physics(engine_names, controller)
            fitness = position_x_true[-1]
            fitnesses.append(fitness)
            position_x_true_list.append(position_x_true)
            position_y_true_list.append(position_y_true)
            angular_position_true_list.append(angular_position_true)
            angular_velocity_true_list.append(angular_velocity_true)
            altitude_sensor_readings_list.append(altitude_sensor_readings) 
            speed_sensor_readings_list.append(speed_sensor_readings)
            angular_position_sensor_readings_list.append(angular_position_sensor_readings)
            angular_velocity_sensor_readings_list.append(angular_velocity_sensor_readings)
            altitude_sensor_readings_scaled_list.append(altitude_sensor_readings_scaled)
            speed_sensor_readings_scaled_list.append(speed_sensor_readings_scaled)
            angular_position_sensor_readings_scaled_list.append(angular_position_sensor_readings_scaled)
            angular_velocity_sensor_readings_scaled_list.append(angular_velocity_sensor_readings_scaled)
            engine_thrusts_list.append(engine_thrusts)
            thrust_vectors_list.append(thrust_vectors)
            fuel_masses_list.append(fuel_masses)
        median_fitness_index = np.argsort(fitnesses)[len(fitnesses)//2]
        position_x_true = position_x_true_list[median_fitness_index]
        position_y_true = position_y_true_list[median_fitness_index]
        angular_position_true = angular_position_true_list[median_fitness_index]
        angular_velocity_true = angular_velocity_true_list[median_fitness_index]
        altitude_sensor_readings = altitude_sensor_readings_list[median_fitness_index]
        speed_sensor_readings = speed_sensor_readings_list[median_fitness_index]
        angular_position_sensor_readings = angular_position_sensor_readings_list[median_fitness_index]
        angular_velocity_sensor_readings = angular_velocity_sensor_readings_list[median_fitness_index]
        altitude_sensor_readings_scaled = altitude_sensor_readings_scaled_list[median_fitness_index]
        speed_sensor_readings_scaled = speed_sensor_readings_scaled_list[median_fitness_index]
        angular_position_sensor_readings_scaled = angular_position_sensor_readings_scaled_list[median_fitness_index]
        angular_velocity_sensor_readings_scaled = angular_velocity_sensor_readings_scaled_list[median_fitness_index]
        engine_thrusts = engine_thrusts_list[median_fitness_index]
        thrust_vectors = thrust_vectors_list[median_fitness_index]
        fuel_masses = fuel_masses_list[median_fitness_index]
        fitness = fitnesses[median_fitness_index]
        # Save the data to the appropriate folder:
        if run_save_path is not None:
            save_path = run_save_path
            generation_string = "0"*(4-len(str(GENERATION_COUNTER)))+str(GENERATION_COUNTER)
            if not os.path.basename(save_path)==generation_string:
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
                save_path = os.path.join(save_path, generation_string)
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
            individual_string = "0"*(5-len(str(round(fitness))))+str(round(fitness)) + "_" + "0"*(4-len(str(INDIVIDUAL_COUNTER)))+str(INDIVIDUAL_COUNTER)
            if not os.path.basename(save_path)==individual_string:
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
                save_path = os.path.join(save_path, individual_string)
                os.mkdir(save_path)
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
            controller.save(os.path.join(save_path, "controller.json"))
        return fitness
    return controller_fitness

# Perform the genetic algorithm to find "good" model weights
# resume -- True if resuming a previous run, False if restarting
# NOTE -- tried keras_genetic.breeder.MutationBreeder(), now trying keras_genetic.breeder.RandomWeightBreeder(model, parents_per_generation=3
def search(engine_names, controller, generations=100, population_size=50, n_parents_from_population=4, return_best=2, save_path=None, resume=False):
    # Configure the saving of results to the proper folder
    engine_code = file_manager.get_code_from_engine_names(engine_names)
    if save_path is not None and not resume:
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        if not (engine_code+"_run" in os.path.basename(save_path)):
            subfolders = os.listdir(save_path)
            last_run_number = 0
            for subfolder in subfolders:
                if engine_code+"_run" in subfolder:
                    try:
                        last_run_number = max(int(subfolder[subfolder.find("run")+len("run"):]), last_run_number)
                    except:
                        pass
            run_name = engine_code+"_run" + "0"*(3-len(str(last_run_number+1))) + str(last_run_number+1)
            save_path = os.path.join(save_path, run_name)
            os.mkdir(save_path)
    # Run the evolutionary search
    results = keras_genetic.search(
        model=controller.model,
        evaluator=controller_fitness_wrapper(engine_names, controller, save_path),
        generations=generations,
        population_size=population_size,
        breeder=keras_genetic.breeder.MutationBreeder(), # NOTE -- tried keras_genetic.breeder.MutationBreeder(), could try keras_genetic.breeder.NParentMutationBreeder(n=3)
        n_parents_from_population=n_parents_from_population,
        return_best=return_best,
    )
    model = results.best.load_model()
    controller = controllers.Controller(model=model)
    return model, controller

# Run the evolutionary search
save_path = "Results" if run_name is None else os.path.join("Results", run_name)
model, controller = search(engine_names, controller, generations=GENERATIONS, population_size=POPULATION_SIZE, n_parents_from_population=2, save_path=save_path, resume=run_name is not None)
external_control.external_control(engine_names, controller)