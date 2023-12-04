from matplotlib import pyplot as plt
import visualization
import file_manager

import statistics
import argparse
import os

DEFAULT_RUN_NAME = "-P-UD_run003"   # Previously "BPGUD_run006", then "-PGUD_run002"

def single(generation, individual, run_name=DEFAULT_RUN_NAME):
    visualization.visualize_simulation_run(generation=generation, individual=individual, run_name=run_name)

def complete(generation, run_name):
    min_fitness_individual, first_quartile_fitness_individual, median_fitness_individual, third_quartile_fitness_individual, max_fitness_individual = summarize_generation(generation, run_name)
    visualization.visualize_simulation_run(generation=generation, individual=min_fitness_individual, run_name=run_name)
    visualization.visualize_simulation_run(generation=generation, individual=first_quartile_fitness_individual, run_name=run_name, details_offset=1)
    visualization.visualize_simulation_run(generation=generation, individual=median_fitness_individual, run_name=run_name, details_offset=2)
    visualization.visualize_simulation_run(generation=generation, individual=third_quartile_fitness_individual, run_name=run_name, details_offset=3)
    visualization.visualize_simulation_run(generation=generation, individual=max_fitness_individual, run_name=run_name, details_offset=4)

def fitness(run_name=DEFAULT_RUN_NAME):
    def get_generation_fitnesses(generation, run_name=DEFAULT_RUN_NAME):
        generation_path, individual_path = file_manager.find_path(generation=generation, individual=1, run_name=run_name)
        individual_paths = [folder for folder in os.listdir(generation_path) if ("_" in folder and "store" not in folder.lower())]
        def get_fitness_from_folder_name(folder_name):
            if "-" in folder_name:
                fitness = -1 * int(folder_name.split("_")[0].split("-")[1])
            else:
                fitness = int(folder_name.split("_")[0])
            return fitness
        return [get_fitness_from_folder_name(folder) for folder in individual_paths]
    generation_path, _ = file_manager.find_path(generation=0, individual=1, run_name=run_name)
    run_path = os.path.dirname(generation_path)
    fitnesses = []
    generations = []
    for generation_path in os.listdir(run_path):
        if "store" in generation_path.lower():
            continue
        generations.append(int(os.path.basename(generation_path)))
        fitnesses.append(get_generation_fitnesses(int(os.path.basename(generation_path)), run_name))

    sorted_fitnesses = sorted(list(zip(generations, fitnesses)), key=lambda x: x[0])
    fitnesses = [fit[1] for fit in sorted_fitnesses]
    plt.boxplot(fitnesses, positions=list(range(len(fitnesses))), vert=True, patch_artist=True, boxprops={"facecolor":"yellow"})
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness Of Rocket Population Vs. Generation Number')
    plt.show()

# Finds the individuals with the minimum, Q1, median, Q3, and maximum fitness scores and returns those individual IDs.
def summarize_generation(generation, run_name=DEFAULT_RUN_NAME):
    generation_path, individual_path = file_manager.find_path(generation=generation, individual=1, run_name=run_name)
    individual_paths = [folder for folder in os.listdir(generation_path) if ("_" in folder and "store" not in folder.lower())]
    def get_fitness_and_ID_from_folder_name(folder_name):
        if "-" in folder_name:
            fitness = -1 * int(folder_name.split("_")[0].split("-")[1])
        else:
            fitness = int(folder_name.split("_")[0])
        individual_ID = int(folder_name.split("_")[1])
        return fitness, individual_ID
    individuals_sorted = sorted([get_fitness_and_ID_from_folder_name(folder) for folder in individual_paths], key=lambda x: x[0])
    min_fitness, min_fitness_individual = individuals_sorted[0]
    max_fitness, max_fitness_individual = individuals_sorted[-1]
    median_fitness, median_fitness_individual = individuals_sorted[len(individuals_sorted)//2]
    first_quartile_fitness, first_quartile_fitness_individual = individuals_sorted[len(individuals_sorted)//4]
    third_quartile_fitness, third_quartile_fitness_individual = individuals_sorted[3*len(individuals_sorted)//4]
    print("Minimum fitness: ", min_fitness, f"(individual {min_fitness_individual})")
    print("1st Quartile fitness: ", first_quartile_fitness, f"(individual {first_quartile_fitness_individual})")
    print("Median fitness: ", median_fitness, f"(individual {median_fitness_individual})")
    print("3rd Quartile fitness: ", third_quartile_fitness, f"(individual {third_quartile_fitness_individual})")
    print("Maximum fitness: ", max_fitness, f"(individual {max_fitness_individual})")
    return min_fitness_individual, first_quartile_fitness_individual, median_fitness_individual, third_quartile_fitness_individual, max_fitness_individual

def main():
    parser = argparse.ArgumentParser(description='Arg parser.')
    parser.add_argument('-f', '--function', type=str, default="single", help='What function to run via the main method. Use single to visualize a single run; complete to visualize a complete run (5 visuals per generation); fitness to plot the fitness scores of every generation in the run')
    parser.add_argument('-g', '--generation', type=int, default=0, help='Generation number to pull run from')
    parser.add_argument('-i', '--individual', type=int, default=0, help='Individual number to pull run from')
    parser.add_argument('-r', '--run_name', type=str, default=DEFAULT_RUN_NAME, help='Run name to pull an individual run from')

    args = parser.parse_args()
    if args.function == "single":
        single(args.generation, args.individual, args.run_name)
    elif args.function == "complete":
        complete(args.generation, args.run_name)
    elif args.function == "fitness":
        fitness(args.run_name)

if __name__ == "__main__":
    main()