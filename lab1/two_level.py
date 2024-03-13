import m5                   # import the m5 (gem5) library created when gem5 is built
from m5.objects import *    # import all of the SimObjects
import argparse
from cache import *
from utils import *

# some variables
target_isa = m5.defines.buildEnv['TARGET_ISA']

parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("binary", default="", nargs="?", type=str,
                    help="Path to the binary to execute.")
parser.add_argument("--l1i_size",
                    help=f"L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size",
                    help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size",
                    help="L2 cache size. Default: 256kB.")

options = parser.parse_args()

# create the system we are going to simulate
system = System()

# set the clock frequency of the system
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# set up the memory
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# create a simple cpu
system.cpu = TimingSimpleCPU()
# create L1 cache for the cpu
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
# connect L1 cache to the cpu
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# We can’t directly connect the L1 caches to the L2 cache since the L2 cache only expects a single port to connect to it. Therefore, we need to create an L2 bus to connect our L1 caches to the L2 cache
system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# create our L2 cache and connect it to the L2 bus and the memory bus.
system.l2cache = L2Cache()
system.l2cache.connectCPUSideBus(system.l2bus)
system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)

# create an interrupt controller for the CPU and connect it to the membus
system.cpu.createInterruptController()
# Connecting the PIO and interrupt ports to the memory bus is an x86-specific requirement. Other ISAs (e.g., ARM) do not require these 3 extra lines.
if target_isa == "x86":
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(options.binary)

# Create a process for a simple "Hello World" application
process = Process()
process.cmd = [options.binary]
system.cpu.workload = process
system.cpu.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system = False, system = system)

# goes through all of the SimObjects we’ve created in python and creates the C++ equivalents
m5.instantiate()

print(colorize_text(
    'Beginning simulation! Target ISA = {}'.format(target_isa),
    color_yellow))
exit_event = m5.simulate()

print(colorize_text(
    'Exiting @ tick {} because {}'
    .format(m5.curTick(), exit_event.getCause()),
    color_green))
