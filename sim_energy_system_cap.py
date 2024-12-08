## Script Name: sim_energy_system_cap.py

## Usage: python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s

## Parameters:
# sa_m2: Solar Cell Surface Area
# eff: Solar Cell Efficiency
# voc: Solar Array open circuit voltage
# c_f: energy buffer capacitance
# r_esr: capacitor effective series resistance
# q0_c: initial charge of capacitor
# p_on_w: power draw during operation
# v_thresh: voltage threshold for power off
# dt_s: Simulation time step in seconds
# dur_s: Simulation duration in seconds

## Output: Simulates charging and discharging of solar cells over a given period of time

## Written by Carl Hayden

## Importing Libraries
import math
import sys # argv
import csv

## Defining Other Dependent Functions
def calc_solar_current(Irr_w_m2, sa_m2, eff, voc):
    return Irr_w_m2 * sa_m2 * eff / voc

def calc_node_discr(q_c, c_f, i_a, esr_ohm, power_w):
    return (q_c/c_f + i_a*r_esr)**2 - 4*power_w*r_esr

def calc_node_voltage(disc, q_c, c_f, i_a, esr_ohm):
    return (q_c/c_f + i_a*esr_ohm + math.sqrt(disc))/2

## Defining Constants
Irr_w_m2 = 1366.1 # Solar irradiance in W/m^2

## Initialize Script Arguments
sa_m2 = float('nan')
eff = float('nan')
voc = float('nan')
c_f = float('nan')
r_esr = float('nan')
q0_c = float('nan')
p_on_w = float('nan')
v_thresh = float('nan')
dt_s = float('nan')
dur_s = float('nan')

## Parse Script Arguments
if len(sys.argv)==11:
    sa_m2 = float(sys.argv[1])
    eff = float(sys.argv[2])
    voc = float(sys.argv[3])
    c_f = float(sys.argv[4])
    r_esr = float(sys.argv[5])
    q0_c = float(sys.argv[6])
    p_on_w = float(sys.argv[7])
    v_thresh = float(sys.argv[8])
    dt_s = float(sys.argv[9])
    dur_s = float(sys.argv[10])

else:
    print(\
        'Usage: '\
        'python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh dt_s dur_s'\
    )
    exit()

## Main Script
# Initializing Variables
isc_a = calc_solar_current(Irr_w_m2, sa_m2, eff, voc)
i1_a = isc_a
qt_c = q0_c
p_mode_w = p_on_w
t_s = 0.0

# Calculating Initial Node Discriminant
node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)

if node_discr < 0.0:
    p_mode_w = 0.0
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)

# Calculating Initial Node Voltage
node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)
if voc <= node_v and i1_a != 0.0:
    i1_a = 0.0
if node_v < v_thresh:
    p_mode_w = 0.0


# Iterative Loop
log = []
while t_s < dur_s:  # Run until the time exceeds duration
    i3_a = p_mode_w / node_v if node_v != 0 else 0
    qt_c += (i1_a - i3_a) * dt_s
    if qt_c < 0.0:
        qt_c = 0.0
    if 0 <= node_v < voc:
        i1_a = isc_a
    else:
        i1_a = 0.0
    if p_mode_w == 0.0 and node_v >= voc:
        p_mode_w = p_on_w
    node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
    if node_discr < 0.0:
        p_mode_w = 0.0
        node_discr = calc_node_discr(qt_c, c_f, i1_a, r_esr, p_mode_w)
    node_v = calc_node_voltage(node_discr, qt_c, c_f, i1_a, r_esr)
    if voc <= node_v and i1_a != 0.0:
        i1_a = 0.0
    if node_v < v_thresh:
        p_mode_w = 0.0
    log.append([t_s, node_v])  # Storing time and node voltage for the CSV
    t_s += dt_s

# Writing to local CSV file
with open('./log.csv', mode='w', newline='') as outfile:
    csvwriter = csv.writer(outfile)
    csvwriter.writerow(['t_s', 'volts'])
    for e in log:
        csvwriter.writerow(e)

print("I'm Done!")