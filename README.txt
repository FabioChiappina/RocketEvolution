This submission contains all of the python code used to run the evolutionary algorithm.

Keyboard control can be run with the following command:
python keyboard_control.py
The rocket can then be controlled using the following keys:
B - Turn on/off the bully engine
G - Turn on/off the greedy engine
P - Turn on/off the patient engine
U - Turn on/off the upsteering engine
D - Turn on/off the downsteering engine

The genetic algorithm can be run by using:
python genetic_search.py 
This will create a new folder inside the "Results" directory and save the results of the genetic search there. Note that if this errors, you may need to create a new directory named "Results" and ensure it's inside the same directory as these .py files. Also note that you can configure the engines you're using by modifying the "engine_names" variable at the top of the genetic_search.py file.

Finally, various visualizations can be run via main.py. Note you can configure the name of the run you want to visualize at the top of main.py (in the variable "DEFAULT_RUN_NAME").
python main.py -f single -g 0 -i 8
    Creates a visualization for a single individual in a single generation. Specify individual and generation with the -g and -i flags (in this example, generation 0 and individual 8). Visualizations are saved within that individual's corresponding results folder.
python main.py -f complete -g 1
    Creates a visualization for five individuals in a single generation -- the min, 1st quartile, median, 3rd quartile, and max fitness individuals. Visualizations are saved within those individuals' corresponding results folders.

