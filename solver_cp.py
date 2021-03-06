import os, time, json, argparse
from CP.utils import *

parser = argparse.ArgumentParser(description='Argument parser')
parser.add_argument("--model", help="[base]: assume each piece fixed, [general]: pieces can rotate", required = True, type=str)
parser.add_argument("--override", help="[default: False] set to true to recompute and override previously solved solutions", required = False, default=False, type=bool)
parser.add_argument("--solve", help="[default: all] provide the instances you want to solve, separated by a comma. E.g. 8x8,10x10,20x20", required = False, default=None, type=str)
args = parser.parse_args()

MODEL = f"{args.model.lower()}"
DATA_PATH = "./CP/__data__"
MODEL_PATH = f"./CP/{MODEL}/{MODEL}.mzn"
MINIZINC = json.load(open("config.json"))["CP"]
SOLUTIONS_PATH = f"./CP/{MODEL}/solutions"
PLOTS_PATH = f"./CP/{MODEL}/plots"
LOG_PATH = f"./CP/{MODEL}/log.json"
data_files = [name for name in os.listdir(DATA_PATH) if ".dzn" in name]

# # # # # SETUP # # # # #

print("\n* * * * CP solver * * * *\n")

# setup the environment
for folder_name in [SOLUTIONS_PATH, PLOTS_PATH]:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"[SETUP]\tFolder '{folder_name}' created.")
    else:
        print(f"[SETUP]\tFolder '{folder_name}' already exists.")

try:
    with open(LOG_PATH, "r") as f:
        log = json.load(f)
        print(f"[SETUP]\tLog loaded. {len(log.keys())} solutions found.")
except:
    open(LOG_PATH, "w")
    log = {}
    print("[SETUP]\tLog created. ")
    pass

print(f"[SETUP]\tmodel: {args.model.upper()}")
print("Instances to be solved:")
to_solve = args.solve.split(",") if args.solve != None else None
if to_solve == None:
    print(" - all")
else:
    print(to_solve)
input("\nPress ENTER to start\n\n")

# # # # # # # FIND SOLUTIONS # # # # # # # # #

for i, file_name in enumerate(data_files):

    instance_name = file_name.replace(".dzn", "")

    if to_solve != None and instance_name not in to_solve:
        continue
    
    solution_file = f"{SOLUTIONS_PATH}/solution_{instance_name}.txt"
    print("\n\n--- Instance", file_name, " ---")
    if instance_name in log and not args.override: 
        print(f"\tAlready solved ({str(log[instance_name]).upper()})")
        continue

    # - - - - - - - init log
    log[instance_name] = "aborted"
    with open(LOG_PATH, "w") as f: json.dump(log, f)

    #  - - - - - - solve the instnace
    print(f"\tSolving...\t[start time {time.strftime('%H:%M')}]")
    t0 = time.time()
    os.system(f"{MINIZINC} --solver-time-limit 1800000 --solver Gecode {MODEL_PATH} {DATA_PATH}/{file_name} > {solution_file}")
    # os.system(f"{MINIZINC} --solver Gecode {MODEL_PATH} {DATA_PATH}/{file_name} > {solution_file}")
    result = round(time.time() - t0, 3)
    print(f"\tsolved in \t[{result} s]")
    print("\tresult saved to\t", solution_file)
    
    # - - - - - - plot the solution
    try:
        plot_name = plot_solution(solution_file, show=False, export_folder=PLOTS_PATH, verbose=False)
        print(f"\tplot saved as\t'{plot_name}'")
    except:
        print(f"Impossible to show the solution: Incorrect/Unsatisfiable")
        result = "unsatisfiable"

    # - - - - - - - save log
    log[instance_name] = result
    with open(LOG_PATH, "w") as f: json.dump(log, f)
   
# --- rename solutions files as required
import os
for name in os.listdir(SOLUTIONS_PATH):
    new_name = name.replace(".txt", "").split("_")[1] + "-out.txt"
    os.rename(f"{SOLUTIONS_PATH}/{name}", f"{SOLUTIONS_PATH}/{name}")

print("\n\n", "-"*20,"All the instance have been solved.")
