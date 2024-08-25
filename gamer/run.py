import os
import sys

# design_names = [
#     "ispd18_test5", "ispd19_test7", "ispd19_test7_metal5"
# ]
design_names = {
    "ispd2024": 
    ["ariane133_68", "ariane133_51", "nvdla", "mempool_tile", "bsg_chip", "mempool_group"], #, "mempool_cluster"], #, "mempool_cluster_large"],
    "iccad2019": 
        #["ispd18_test1", "ispd18_test2", "ispd18_test3", "ispd18_test4", "ispd18_test5", "ispd18_test5_metal5", 
    #"ispd18_test7", "ispd18_test8", "ispd18_test8_metal5", 
    #"ispd19_test1", "ispd19_test5", "ispd19_test6", "ispd19_test7", "ispd19_test7_metal5"]
    ["ispd18_test1", "ispd18_test2", "ispd18_test3", "ispd18_test4", "ispd18_test5", "ispd18_test5_metal5", 
    "ispd18_test6", "ispd18_test7", "ispd18_test8", "ispd18_test8_metal5", "ispd18_test9", 
    "ispd18_test10", "ispd18_test10_metal5", "ispd19_test1", "ispd19_test2", "ispd19_test3", 
    "ispd19_test4", "ispd19_test5", "ispd19_test6", "ispd19_test7", "ispd19_test7_metal5", 
    "ispd19_test8", "ispd19_test8_metal5", "ispd19_test9", "ispd19_test9_metal5", "ispd19_test10"]
}

benchmark = "iccad2019" # "ispd2024" or "iccad2019"
## get benchmark name from argx
if len(sys.argv) == 2:
    benchmark = sys.argv[1]
case_dir = f'./data/raw/{benchmark}'
out_dir = './output'

def run_case(design_name):
    print(f"Running for {design_name}")
    lef_file = f'{case_dir}/lef/Nangate.lef' if benchmark == "ispd2024" else f'{case_dir}/lefdef/{design_name}/{design_name}.input.lef'
    def_file = f'{case_dir}/def/{design_name}.def' if benchmark == "ispd2024" else f'{case_dir}/lefdef/{design_name}/{design_name}.input.def'
    command = f"bash -c 'python ./main_test_gr.py -lef {lef_file} -def {def_file} -output {out_dir}/{design_name}.PR_output |& tee {out_dir}/{design_name}.log'"
    print(f"Run cmd: {command}")
    os.system(command)

if __name__ == "__main__":
    for design in design_names[benchmark]:
        run_case(design)
