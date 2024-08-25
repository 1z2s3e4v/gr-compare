#!/bin/bash
#data_list=("ariane133_68" "ariane133_51" "nvdla" "mempool_tile" "bsg_chip" "mempool_group" "mempool_cluster" "mempool_cluster_large")
data_list=("ariane_68_rank" "bsg_chip_rank" "nvdla_rank" "mempool_tile_rank" "mempool_group_rank" "mempool_cluster_ranking" "tera_cluster_rank")
# data_list=("ariane133_51")
input_path="../benchmarks/raw/ispd2024/Simple_inputs"
# output_path="../benchmarks/raw/ispd2024/example_output"
output_path="../output"
log_path="./log"
mkdir -p ./$log_path
if [ $# -eq 1 ]; then # run one case
    data=${data_list[$1]}
    log_file=$log_path/$data.log
    echo "data: $data"
    ./evaluator $input_path/$data.cap $input_path/$data.net $output_path/$data.PR_output 2>&1 | tee $log_file
else
    for data in "${data_list[@]}"
    do
        # run the whole framework
        echo "data: $data"
        ./evaluator $input_path/$data.cap $input_path/$data.net $output_path/$data.PR_output
    done
fi


