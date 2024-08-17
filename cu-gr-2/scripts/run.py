#!/usr/bin/env python3

import argparse
import os
import datetime
from run_base import *
from visualize_heatmap import visualize

# constants
binary = 'route'

# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-lef', '--lef', default='')
parser.add_argument('-def', '--deff', default='')
parser.add_argument('-cap', '--cap', default='')
parser.add_argument('-net', '--net', default='')
parser.add_argument('-output', '--output', default='')
parser.add_argument('-m', '--mode', choices=modes)
parser.add_argument('-s', '--steps', choices=['route', 'eval', 'view', 'nano'], nargs='+', default=['route'])
parser.add_argument('-p', '--benchmark_path')
parser.add_argument('-t', '--threads', type=int, default=8)
parser.add_argument('-i', '--rrr_iters', type=int)
parser.add_argument('-e', '--eval_all_rrr_iters', action='store_true')
parser.add_argument('-o', '--others', default='')
parser.add_argument('-l', '--log_dir')
args = parser.parse_args()
cmd_suffix = args.others
if args.eval_all_rrr_iters:
    cmd_suffix += ' -rrrWriteEachIter 1'

if args.rrr_iters is not None:
    cmd_suffix += ' -rrrIters {}'.format(args.rrr_iters)

# seleted benchmarks
bm_lef = args.lef
bm_def = args.deff
bm_cap = args.cap
bm_net = args.net
bm_out = args.output
bm = os.path.basename(args.output).split('.')[0]

# mode cmd_prefix
cmd_prefix = mode_prefixes[args.mode]
if args.mode == 'valgrind':
    print('Please make sure the binary is not compiled with static linking to avoid false alarm')

# run
if args.log_dir is None:
    now = datetime.datetime.now()
    log_dir = 'run{:02d}{:02d}'.format(now.month, now.day)
else:
    log_dir = args.log_dir

run('mkdir -p {}'.format(log_dir))
print('The following benchmark will be ran: ', bm)

def route():
    guide_file = '{0}/{1}'.format(bm_log_dir, bm_out)
    log_file = '{0}/{1}.log'.format(bm_log_dir, bm)

    run('{cmd_prefix} ./{0} -lef {1} -def {2} -threads {3} -output {4} {6} |& tee {5}'.format(
        binary, bm_lef, bm_def, args.threads, guide_file, log_file, cmd_suffix, cmd_prefix=cmd_prefix))

    if args.mode == 'gprof':
        run('gprof {} > {}.gprof'.format(binary, bm))
        run('./gprof2dot.py -s {0}.gprof | dot -Tpdf -o {0}.pdf'.format(bm))
    
    # visualize grid graph heatmap
    heatmap_name = 'heatmap.txt'
    if os.path.exists(heatmap_name):
        visualize(heatmap_name)
        run('rm {}'.format(heatmap_name))
        # update figs
        run('rm -rf {}/figs'.format(bm_log_dir))
        run('mv -f figs {}'.format(bm_log_dir))
        
    run('mv *.solution.guide* *.solution.def* *.gprof *.pdf {} 2>/dev/null'.format(bm_log_dir))

bm_log_dir = '{}/{}'.format(log_dir, bm)
run('mkdir -p {}'.format(bm_log_dir))
route()