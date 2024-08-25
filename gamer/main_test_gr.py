# main_test_gr.py
import torch
import time
import sys

from utils import IOParser
from cpp_to_py import gpugr
from src import Flute
from src.core.route_force import calc_gr_wl_via, estimate_num_shorts

num_threads = 20
gpu_id = 0
Flute.register(num_threads)
torch.cuda.synchronize("cuda:{}".format(gpu_id))

# 1) Benchmark Setting
for i, s in enumerate(sys.argv):
    if s == "-lef": lef_file = sys.argv[i+1]
    if s == "-def": def_file = sys.argv[i+1]
    if s == "-output": out_file = sys.argv[i+1]
start_index = lef_file.find("data/raw/") + len("data/raw/")
end_index = lef_file.find("/", start_index)
design_set = lef_file[start_index:end_index] if start_index != -1 else "unknown"
design_name = out_file.split('/')[-1]
dot_index = design_name.rfind('.')
design_name = design_name[:dot_index]

params = {
    "benchmark": "iccad2019",
    "lef": lef_file,
    "def": def_file,
    "design_name": design_name,
}
route_guide_file = out_file

# 2) LEF/DEF Parser
print("--- Start GR ---")
start_gr_time = time.time()
parser = IOParser()
rawdb, gpdb = parser.read(
    params, verbose_log=True, lite_mode=True, random_place=False, num_threads=num_threads
)

# 3) Construct Global Routing Database and Run GGR
gpugr.load_gr_params(
    {
        "device_id": gpu_id,
        "route_xSize": 0,
        "route_ySize": 0,
        "rrrIters": 1,
        "route_guide": route_guide_file,
    }
)
grdb = gpugr.create_grdatabase(rawdb, gpdb)
routeforce = gpugr.create_routeforce(grdb)
routeforce.run_ggr()
end_gr_time = time.time()
print("--- End GR ---")

# 4) Report Global Routing Statistics
skip_m1_route = True
m1direction = gpdb.m1direction()  # 0 for H, 1 for V, metal1's layer idx is 0
hId = 1 if m1direction else 0
vId = 0 if m1direction else 1
if skip_m1_route:
    hId = hId + 2 if hId == 0 else hId
    vId = vId + 2 if vId == 0 else vId

dmd_map, wire_dmd_map, via_dmd_map = routeforce.dmd_map()
cap_map: torch.Tensor = routeforce.cap_map()

cg_mapH = dmd_map[hId::2].sum(dim=0) / cap_map[hId::2].sum(dim=0)
cg_mapV = dmd_map[vId::2].sum(dim=0) / cap_map[vId::2].sum(dim=0)
cg_mapHV = torch.stack((cg_mapH, cg_mapV))
cg_mapHV = torch.where(cg_mapHV > 1, cg_mapHV - 1, 0)

numOvflNets = routeforce.num_ovfl_nets()
gr_wirelength, gr_numVias = calc_gr_wl_via(grdb, routeforce)
gr_numShorts = estimate_num_shorts(routeforce, gpdb, cap_map, wire_dmd_map, via_dmd_map)

gr_time = end_gr_time - start_gr_time

print(
    "#OvflNets: %d, GR WL: %d, GR #Vias: %d, #EstShorts: %d | GR Time: %.4f"
    % (numOvflNets, gr_wirelength, gr_numVias, gr_numShorts, gr_time)
)
