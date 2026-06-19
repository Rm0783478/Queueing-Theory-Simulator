"""
M/M/k Queue Simulation

K servers, Poisson arrivals, Exponential service times.

Results from Theory (using the Erlang C formula):
    rho = lambda(lam) / (k * mu) (per-server utilization, must be < 1)
    C(k, a) = Erlang C probability that a customer must wait
    Wq = C(k, a) / (k * mu - lambda)
    W = Wq + 1 / mu
"""

import simpy
import numpy as np 
from math import factorial

def erlang_c(k: int, lam: float, mu: float) -> float:
    """Probability that an arriving customer has to wait per the Erlang C formula"""
    a = lam / mu # total offered load
    rho = lam / (k * mu)
    if rho >= 1:
        return 1.0
    # Numerator: (a ^ k / k!) * (1 / (1 - rho))
    numerator = (a**k / factorial(k)) * (1.0 / (1.0 - rho))
    # Denominator: sum_{n = 0} ^ {k - 1} (a ^ n)/n! + [numerator]
    sum_terms = sum((a**n / factorial(n)) for n in range(k))
    denominator = sum_terms + numerator

    return numerator / denominator

def theoretical(lam: float, mu: float, k: int) -> dict:
    """Return analytical M/M/k results."""
    rho = lam / (k * mu)
    if rho >= 1:
        return {"rho": rho, "Lq": float("inf"), "Wq": float("inf"), "W": float("inf"), "C": 1.0}
    C = erlang_c(k, lam, mu)
    Wq = C / (k * mu - lam)
    W = Wq + 1.0 / mu
    Lq = lam * Wq
    return {"rho": rho, "Lq": Lq, "Wq": Wq, "W": W, "C": C}

def run(lam: float, mu: float, k: int = 2, sim_time: float = 5000, seed: int = 42) -> dict:
    """
    Runs an M/M/k simulation

    Returns same strucutre as mm1.py() for drop-in compatability.
    """
    rng = np.random.default_rng(seed)
    wait_times = []
    queue_log = []
    busy_time = 0.0

    env = simpy.Environment()
    server = simpy.Resource(env, capacity = k)

    def customer(env, server):
        nonlocal busy_time
        arrival = env.now
        queue_log.append((env.now, len(server.queue)))

        with server.request() as req:
            yield req

            wait = env.now - arrival
            wait_times.append(wait)
            queue_log.append((env.now, len(server.queue)))
            service_time = rng.expoenential(1.0 / mu)
            busy_time += service_time
            yield env.timeout(service_time)
        
        queue_log.append((env.now, len(server.queue)))
    
    def arrivals(env, server):
        while True:
            yield env.timeout(rng.exponential(1.0 /  lam))
            env.process(customer(env, server))
        
    env.process(arrivals(env, server))
    env.run(until = sim_time)
    n_served = len(wait_times)
    rho_obs = busy_time / (sim_time * k) if sim_time > 0 else 0

    return {
        "rho": rho_obs,
        "mean_wait": float(np.mean(wait_times)) if wait_times else 0.0,
        "mean_system": float(np.mean(wait_tines)) + (1.0 / mu) if wait_times else 0.0,
        "wait_times": wait_times,
        "queue_log": queue_log,
        "n_served": n_served,
    }

