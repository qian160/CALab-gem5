# import the m5 (gem5) library created when gem5 is built
import m5
# import all of the SimObjects
from m5.objects import *
from utils import *

# some variables
target_isa = m5.defines.buildEnv['TARGET_ISA']
binary = os.path.join('tests/test-progs/hello/bin/', target_isa.lower(), 'linux/hello')

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

# create a memory bus
system.membus = SystemXBar()

# connect the MemObjects
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

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
system.workload = SEWorkload.init_compatible(binary)

# Create a process for a simple "Hello World" application
process = Process()
process.cmd = [binary]
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
