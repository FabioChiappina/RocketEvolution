import os
import json

import controllers
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def get_code_from_engine_names(engine_names):
    engine_names = [name.lower() for name in engine_names]
    code = ""
    if "bullyengine" in engine_names:
        code += "B"
    else:
        code += "-"
    if "patientengine" in engine_names:
        code += "P"
    else:
        code += "-"    
    if "greedyengine" in engine_names:
        code += "G"
    else:
        code += "-"
    if "upsteeringengine" in engine_names:
        code += "U"
    else:
        code += "-"
    if "downsteeringengine" in engine_names:
        code += "D"
    else:
        code += "-"
    return code

def get_engine_names_from_code(engine_name_code):
    engine_names = []
    ["BullyEngine", "PatientEngine", "GreedyEngine", "UpSteeringEngine", "DownSteeringEngine"]
    if "B" in engine_name_code:
        engine_names.append("BullyEngine")
    if "P" in engine_name_code:
        engine_names.append("PatientEngine")
    if "G" in engine_name_code:
        engine_names.append("GreedyEngine")
    if "U" in engine_name_code:
        engine_names.append("UpSteeringEngine")
    if "D" in engine_name_code:
        engine_names.append("DownSteeringEngine")
    return engine_names

# Returns true if the input is a code describing which engines are present on a given rocket (e.g., "B-GU-"); false otherwise.
def is_engine_code(engine_code):
    if not isinstance(engine_code, str):
        return False
    if len(engine_code) != 5:
        return False
    engine_code = [c.lower() for c in engine_code]
    if any([c not in ["-","b","p","g","u","d"] for c in engine_code]):
        return False
    return True

def load_run(generation, individual, run_name=None, engines=None, results_path="Results"):
    if engines is None and run_name is None:
        raise ValueError("Must input a non-None string for either engines or run_name.")
    if isinstance(run_name, str) and len(run_name.split("_"))==2 and is_engine_code(run_name.split("_")[0]):
        run_path = run_name
    else:
        if engines is None:
            print(len(run_name.split("_")))
            if type(run_name)==str and len(run_name.split("_"))==2:
                engines = run_name.split("_")[0]
            else:
                raise ValueError("Input engines is None, and engines not found in the input run_name.")
        if isinstance(engines, list):
            engines = get_code_from_engine_names(engines)
        elif not isinstance(engines, str):
            raise ValueError("Input engines must be a string.")
        if run_name is None:
            run_name = 1    
        if not (isinstance(run_name, str) or isinstance(run_name, int)):
            raise ValueError("Input run_name must be a string or integer.")  
        if isinstance(run_name, str):
            if len(run_name.split("_"))==2:
                run_name = run_name.split("_")[1]
            run_name = int(run_name.replace("run", ""))
        run_path = engines+"_run" + "0"*(3-len(str(run_name))) + str(run_name)
    run_path = os.path.join(results_path, run_path, "0"*(4-len(str(generation)))+str(generation))
    individual_path = None
    if not os.path.exists(run_path):
        raise ValueError("The path specified by the run_name and/or engines and the generation number does not exist.")
    for subfolder in os.listdir(run_path):
        if "-" not in subfolder:
            continue
        if int(subfolder.split("-")[1])==int(individual):
            individual_path = os.path.join(run_path, subfolder)
            break
    if individual_path is None:
        raise ValueError("Individual not found.")
    with open(os.path.join(individual_path, "run_data.json"), "r") as json_file:
        simulation_data = json.load(json_file)
    controller = controllers.Controller.load(os.path.join(individual_path, "controller.json"))
    engine_names = get_engine_names_from_code(os.path.dirname(os.path.dirname(individual_path)).split("_")[0])
    return simulation_data, controller, engine_names