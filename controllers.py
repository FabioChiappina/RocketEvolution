import numpy as np
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# A class defining a rocket engine controller that uses sensors (e.g., position, speed, orientation, ...), engine thrusting percentages, and fuel mass to determine which of its engines it should fire at any given time.
class Controller:
    def __init__(self, n_sensors=4, n_engines=0, hidden_layer_sizes=[5,5], verbose=False, model=None):
        self.n_sensors = n_sensors
        self.n_engines = n_engines
        if model is None:
            model = keras.Sequential()
            model.add(keras.Input(shape=(None,self.n_sensors+self.n_engines+1)))
            for ls in hidden_layer_sizes:
                model.add(layers.Dense(ls))
            model.add(layers.Dense(n_engines, activation="sigmoid")) 
            model.compile()
        else:
            self.n_engines = max(0, model.input_shape[-1] - n_sensors - 1)
        self.model = model
        if verbose:
            model.summary()

    def predict(self, sensor_readings, engine_thrusts, fuel_masses):
        if type(sensor_readings)==list:
            sensor_readings = np.array(sensor_readings)
        if type(engine_thrusts)==list:
            engine_thrusts = np.array(engine_thrusts)
        if type(fuel_masses)==int or type(fuel_masses)==float:
            fuel_masses = [fuel_masses]
        if type(fuel_masses)==list:
            fuel_masses = np.array(fuel_masses)
        if len(fuel_masses.shape)==1 and len(sensor_readings.shape)>1:
            fuel_masses = np.expand_dims(fuel_masses, 0)
        if sensor_readings.shape[0] != self.n_sensors:
            raise ValueError(f"Input sensor_readings ({sensor_readings.shape[0]}) must have shape equal to self.n_sensors ({self.n_sensors}).")
        if engine_thrusts.shape[0] != self.n_engines:
            raise ValueError(f"Input engine_thrusts ({engine_thrusts.shape[0]}) must have shape equal to self.n_engines ({self.n_engines}).")
        input_vector = np.expand_dims(np.concatenate((sensor_readings, engine_thrusts, fuel_masses), axis=0), axis=0)
        return self.model.predict(input_vector, verbose=0)
    
    def save(self, filepath):
        if not filepath.endswith("controller.json"):
            filepath = os.path.join(filepath, "controller.json")
        with open(filepath, "w") as json_file:
            json_file.write(self.model.to_json())
    
    def load(filepath):
        if not filepath.endswith("controller.json"):
            filepath = os.path.join(filepath, "controller.json")
        with open(filepath, "r") as json_file:
            model_json = json_file.read()
            model = keras.models.model_from_json(model_json)
        n_engines = 0
        for folder in filepath.split(os.path.sep):
            if "_run" in folder and len(folder.split("_")[0])==5:
                n_engines = 5 - folder.split("_")[0].count("-")
                break
        input_shape = 0
        for value in model.layers[0].input_shape:
            if value is not None and value>input_shape:
                input_shape = value
        n_sensors = input_shape - 1 - n_engines
        return Controller(n_sensors=n_sensors, n_engines=n_engines, model=model)