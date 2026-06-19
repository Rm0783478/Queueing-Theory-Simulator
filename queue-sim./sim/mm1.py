"""
M/M/1 Queue Simulation

Single server, Poisson arrivals, Exponential service times

Arguments:
lambda: arrival rate (customers/unit time)
mu: rate of service (customers/unit time)
sim_time: how long it takes to run the simulation

Results from Theory (for verification):
rho = lambda / mu (utilization, must be < 1 for stable queue)
Lq = (rho)^2 / (1 - rho) (mean mumber in queue)
Wq = Lq / lambda (mean wait time in queue)
W = Wq + 1 / mu (mean total time in system)
"""
