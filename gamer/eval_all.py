import os
import sys
import subprocess
import csv
import re

design_names = {
    "ispd2024": [
        "ariane133_68", "ariane133_51", "nvdla", "mempool_tile", "bsg_chip", "mempool_group" #, "mempool_cluster", "mempool_cluster_large"
    ], 
    "iccad2019": [
        "ispd18_test1"
        # "ispd18_test1", "ispd18_test2", "ispd18_test3", "ispd18_test4", "ispd18_test5", "ispd18_test5_metal5", 
        # "ispd18_test6", "ispd18_test7", "ispd18_test8", "ispd18_test8_metal5", "ispd18_test9", 
        # "ispd18_test10", "ispd18_test10_metal5", "ispd19_test1", "ispd19_test2", "ispd19_test3", 
        # "ispd19_test4", "ispd19_test5", "ispd19_test6", "ispd19_test7", "ispd19_test7_metal5", 
        # "ispd19_test8", "ispd19_test8_metal5", "ispd19_test9", "ispd19_test9_metal5", "ispd19_test10"
    ]
}

benchmark = "iccad2019" # "ispd2024" or "iccad2019"
## get benchmark name from argx
if len(sys.argv) == 2:
    benchmark = sys.argv[1]

output_csv = 'results-gamer.csv'
case_dir = f'./data/raw/{benchmark}/Simple_inputs'
out_dir = './output'
eval_bin = './evaluate/evaluator'
log_file_path = 'run_all_log'

def run_evaluator(case_names):
    results = []
    for case_name in case_names:
        # prepare .cap and .net
        cap_file = f"{case_dir}/{case_name}.cap"
        net_file = f"{case_dir}/{case_name}.net"
        out_file = f"{out_dir}/{case_name}.PR_output"

        command = f"{eval_bin} {cap_file} {net_file} {out_file}"
        print(f"Running command: {command}")
        # run evaluator and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # check output from evaluator
        output_lines = result.stdout.splitlines()
        parsed_result = parse_evaluator_output(output_lines)
        parsed_result['case_name'] = case_name
        results.append(parsed_result)

        # check runtime from log file
        log_file = out_file.replace(".PR_output", ".log")
        runtime = extract_runtime(log_file)
        parsed_result['runtime'] = runtime

        # check MR results from log file
        mr_runtime = extract_MR_runtime(log_file)
        max_batch_size = extract_max_batch_size(log_file)
        mem_usage = extract_mem_usage(log_file)
        parsed_result['mr_runtime'] = mr_runtime
        parsed_result['max_batch_size'] = max_batch_size
        parsed_result['mem_usage'] = mem_usage

    return results

def parse_evaluator_output(output_lines):
    parsed_result = {
        "wirelength_cost": None,
        "via_cost": None,
        "overflow_cost": None,
        "total_cost": None,
        "open_nets": None
    }
    for line in output_lines:
        if 'wirelength cost' in line:
            parsed_result["wirelength_cost"] = line.split()[-1]
        elif 'via cost' in line:
            parsed_result["via_cost"] = line.split()[-1]
        elif 'overflow cost' in line and 'total cost' not in line:
            parsed_result["overflow_cost"] = line.split()[-1]
        elif 'total cost' in line:
            parsed_result["total_cost"] = line.split()[-1]
        elif 'Number of open nets' in line:
            parsed_result["open_nets"] = line.split()[-1]
    return parsed_result

def extract_MR_runtime(log_file):
    mr_func_time = None
    mr_calc_time = None
    with open(log_file, 'r') as file:
        lines = file.readlines()
    ## find lines matches "[  16.706] INFO: MR Func time 0.6358" and "[  16.706] INFO: MR Cost calc time 0.1285"
    for line in lines:
        mr_func_match = re.match(r"\[\s*\d+\.\d+\] INFO: MR Func time (\d+\.\d+)", line)
        if mr_func_match is not None:
            mr_func_time = mr_func_match.group(1)
        mr_calc_match = re.match(r"\[\s*\d+\.\d+\] INFO: MR Cost calc time (\d+\.\d+)", line)
        if mr_calc_match is not None:
            mr_calc_time = mr_calc_match.group(1)
    if mr_func_time is not None and mr_calc_time is not None:
        return float(mr_func_time)# + float(mr_calc_time)
    else:
        return None

def extract_max_batch_size(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()
    # find the last line which matches "[  16.324] INFO: Max used batch size = 7, Avg used batch size = 3, Full batch num = 0 (0.00%)" and extract the max batch size
    for line in reversed(lines):
        max_batch_size_match = re.match(r"\[\s*\d+\.\d+\] INFO: Max used batch size = (\d+), Avg used batch size = \d+, Full batch num = \d+ \(\d+\.\d+%\)", line)
        if max_batch_size_match is not None:
            return max_batch_size_match.group(1)
    return None
        
def extract_mem_usage(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()
    # find the last line which matched "[   2.600] GPU memory utilization: 4.27 GB (8.99%)" and extract the memory usage
    for line in reversed(lines):
        mem_match = re.match(r"\[\s*\d+\.\d+\] GPU memory utilization: (\d+\.\d+) GB \(\d+\.\d+%\)", line)
        if mem_match is not None:
            return mem_match.group(1)
    return None

def extract_runtime(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()
    for line in reversed(lines):
        time_match = re.match(r"\[\s*\d+\.\d+\] Total GPU GR Time: (\d+\.\d+)", line)
        if time_match is not None:
            return time_match.group(1)
    return None

def write_results_to_csv(results):
    headers = results[0].keys()
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

def add_runtime(results, runtime_results):
    for case in runtime_results:
        case_id = case['run_id']
        results[case_id]['runtime'] = case['runtime']

def main():
    results = run_evaluator(design_names[benchmark])
    write_results_to_csv(results)

if __name__ == "__main__":
    main()