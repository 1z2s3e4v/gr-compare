import os
import subprocess
import argparse
import sys

def run_routing_commands(base_folder):
    # find all the case folders in the base folder
    for case_name in os.listdir(base_folder):
        case_folder = os.path.join(base_folder, case_name)
        
        if os.path.isdir(case_folder):
            # determine the lef and def file paths
            lef_file = os.path.join(case_folder, f"{case_name}.input.lef")
            def_file = os.path.join(case_folder, f"{case_name}.input.def")
            out_file = f"{case_name}.guide"

            # check if the lef and def files exist
            if os.path.isfile(lef_file) and os.path.isfile(def_file):
                command = f"./route -lef {lef_file} -def {def_file} -output {out_file} -thread 8 -transFormatToISPD24 1"
                print(f"Running command: {command}")

                process = subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
                process.communicate()
            else:
                print(f"LEF or DEF file not found for case: {case_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run routing commands for each case folder.")
    parser.add_argument("p", type=str, help="Path to the main folder containing case folders")
    args = parser.parse_args()

    base_folder = args.p ## "benchmarks/iccad2019"
    run_routing_commands(base_folder)