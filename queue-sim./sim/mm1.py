"""
M/M/1 Queue Simulation

Single server, Poisson arrivals, Exponential service times

Arguments:
lambda (lam): arrival rate (customers/unit time)
mu: rate of service (customers/unit time)
sim_time: how long it takes to run the simulation

Results from Theory (for verification):
rho = lambda / mu (utilization, must be < 1 for stable queue)
Lq = (rho)^2 / (1 - rho) (mean mumber in queue)
Wq = Lq / lambda (mean wait time in queue)
W = Wq + 1 / mu (mean total time in system)
"""

import simpy
import numpy as np  

def theoretical(lam: float, mu: float) -> dict:
    """Returns analytical M/M/1 results."""
    rho = lam / mu
    if rho >= 1:
        return {"rho": rho, "Lq": float("inf"), "Wq": float("inf"), "W": float("inf")}
    Lq = rho**2 / (1 - rho)
    Wq = Lq / lam
    W = Wq + 1 / mu
    return {"rho": rho, "Lq": Lq, "Wq": Wq, "W": W}

def run(lam: float, mu: float, sim_time: float = 5000, seed: int = 42) -> dict:
    """
    Runs an M/M/1 simulation.

    Retuns a dict with:
    rho (observed utilization)
    mean_wait (mean time soent waiting in queue)
    mean_system (mean total time in system)
    wait_times (list of individual wait times (for histogram))
    queue_log (list of (time queue_length) tuples (for time-series chart))
    n_served (total customers served)

    """
    rng = np.random_default_rng(seed)

    wait_times = []
    queue_log = [] # this is part of the (time, queue_length) tuple
    busy_time = 0.0
    
    # simpy variables #
    env = simpy.Environment()
    server = simpy.Resource(env, capacity = 1)

    def customer (env, server):
        nonlocal busy_time
        arrival = env.now
        queue_log.append((env.now, len(server.queue)))

        with server.request() as req:
            yield req # wait for error
            wait = env.now - arrival
            wait_times.append(wait)
            queue_log.append((env.now, len(server.queue)))

            # service time ~ exponential (mu)
            servive_time = rng.exponential (1.0 / mu)
            busy_time += serivce_time
            yield env.timeout(service_time)
        
        queue_log.append((env.now, len(server.queue)))
    
    def arrivals(env, server):
        while True:
            # inter-arrival time ~ exponentia (lambda)
            yield env.timeout(rng.expoenential(1.0 / lam))
            env.process(customer(env, server))
    
    env.process(arrivals(env, server))
    env.run(until = sim_time)

    n_served = len(wait_times)
    rho_obs = busy_time / sim_time if sim_time > 0 else 0

    return {
        "rho": rho_obs,
        "mean_wait": float(np.mean(wait_times)) if wait_times else 0.0,
        "mean_system": float(np.mean(wait_times)) + (1.0 / mu) if wait_times else 0.0,
        "wait_times": wait_times,
        "queue_log": queue_log,
        "n_served": n_served,
    }
