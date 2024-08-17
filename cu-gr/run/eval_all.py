import os
import subprocess
import csv
import re

case_names = [
    "ispd18_test1", "ispd18_test2", "ispd18_test3", "ispd18_test4", "ispd18_test5", "ispd18_test5_metal5", 
    "ispd18_test6", "ispd18_test7", "ispd18_test8", "ispd18_test8_metal5", "ispd18_test9", 
    "ispd18_test10", "ispd18_test10_metal5", "ispd19_test1", "ispd19_test2", "ispd19_test3", 
    "ispd19_test4", "ispd19_test5", "ispd19_test6", "ispd19_test7", "ispd19_test7_metal5", 
    "ispd19_test8", "ispd19_test8_metal5", "ispd19_test9", "ispd19_test9_metal5", "ispd19_test10"
]

output_csv = 'results-cugr.csv'
case_dir = '../../cu-gr-2/run/ispd24'
out_dir = './run0723'
eval_bin = './evaluate/evaluator'

def run_evaluator(case_names):
    results = []

    for case_name in case_names:
        # prepare .cap and .net
        cap_file = f"{case_dir}/{case_name}.cap"
        net_file = f"{case_dir}/{case_name}.net"
        
        # 提取数字部分以生成solution路径
        num_match = re.match(r"ispd(\d{2})_test(\d+)", case_name)
        num1, num2 = num_match.groups()
        if "_metal5" in case_name:
            solution_file = f"{out_dir}/{num1[1]}t{num2}m/{case_name}.solution.guide"
        else:
            solution_file = f"{out_dir}/{num1[1]}t{num2}/{case_name}.solution.guide"

        command = f"{eval_bin} {cap_file} {net_file} {solution_file}"
        print(f"Running command: {command}")
        # run evaluator and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # check output from evaluator
        output_lines = result.stdout.splitlines()
        parsed_result = parse_evaluator_output(output_lines)
        parsed_result['case_name'] = case_name
        results.append(parsed_result)

        # check runtime from log file
        log_file = solution_file.replace(".solution.guide", ".log")
        runtime = extract_runtime(log_file)
        parsed_result['runtime'] = runtime

    write_results_to_csv(results)

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

def extract_runtime(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()
        last_line = lines[-1].strip()
        match = re.search(r"\[\s*(\d+\.\d+)\]", last_line)
        if match:
            return match.group(1)
    return None

def write_results_to_csv(results):
    headers = results[0].keys()
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

def main():
    
    run_evaluator(case_names)

if __name__ == "__main__":
    main()
