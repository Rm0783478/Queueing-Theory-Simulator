"""
M/G/1 Queue Simulation

Single server, Poisson arrivals, GENRAL service time distribution.

Supported servcie distributions:
    expoenential (matches M/M/1 (baselines))
    normal (constant-sh service (e.g. ATM, kiosk))
    lognormal (skewed service(e,g. call centers, ER triage))
    uniform (bounded service tine)

Results from theory (using Pollaczek-Khinchine (P-K) formula):
    rho = lambda (lam) * E[S]
    Lq = rho^2 * (1 + C_s^2) / (2 * (1 - rho))
    Wq = Lq / lambda
    W = Wq + E[S]

Clarifications:
    E[S] = mean service time = 1 / mu
    C_s^2 = coefficient of variation squared = Var[S] / E[S]^2
"""

import simpy 
import numpy as np 

DISTRIBUTIONS = ["exponential", "normal", "lognormal", "uniform"]

def _sample_service(rng, dist: str, mu: float, cv: float = 1.0) -> float:
    """Draws one service time sample"""
    mean = 1.0 / mu
    std = cv * mean # std = cv * mean => cv = std/mean

    if dist == "exponential":
        return rng.exponential(mean)
    elif dist == "normal":
        # clamps to (+) values
        return max (1e-6, rng.normal(mean, std))
    elif dist == "lognormal":
        # parametrizes lognormal so E[X] = mean and Std[X] = std
        sigma2 = np.log(1 + (std / mean) ** 2)
        mu_ln = np.log(mean) - sigma2 / 2
        return rng.lognormal(mu_ln, np.sqrt(sigma2))
    elif dist == "uniform":
        # uniform on [mean - std * sqrt(3), mean + std * sqrt(3)] preserves mean & std
        half = std * np.sqrt(3)
        low = max(0, mean - half)
        high = mean + half
        return rng.uniform(low, high)
    else:
        raise ValueError(f"Unknown distribution: {dist}")

def theoretical(lam: float, mu: float, cv: float = 1.0) -> dict:
    """P-K formula for M/G/1."""
    ES = 1.0 / mu
    rho = lam * ES
    if rho >= 1:
        return{"rho": rho, "Lq": float("inf"), "Wq": float("inf"), "W": float("inf")}
    Cs2 = cv **2 # coefficient of variation squared
    Lq = (rho ** 2 * (1 + Cs2)) / (2 * (1 - rho))
    Wq = Lq / lam
    W = Wq + ES
    return{"rho": rho, "Lq": Lq, "Wq": Wq, "W": W}

def run(lam: float, mu: float, dist: str = "exponential", cv: float = 1.0, sim_time: float = 5000, seed: int = 42) -> dict:
    """
    Runs an M/G/1 simulation.

    Arguments:
        lambda (lam) (arrival rate)
        mu (mean service rate (1/E[S]))
        dist (service time distribution (see Distributions))
        cv (coefficient of variation of service time (cv=1 → exponential)
        sim_time (simulation duration)
        seed (random seed)
    """
    rng = np.random.default_rng(seed)

    wait_times = []
    queue_log  = []
    busy_time  = 0.0

    env    = simpy.Environment()
    server = simpy.Resource(env, capacity=1)

    def customer(env, server):
        nonlocal busy_time

        arrival = env.now
        queue_log.append((env.now, len(server.queue)))

        with server.request() as req:
            yield req

            wait = env.now - arrival
            wait_times.append(wait)
            queue_log.append((env.now, len(server.queue)))

            service_time = _sample_service(rng, dist, mu, cv)
            busy_time += service_time
            yield env.timeout(service_time)

        queue_log.append((env.now, len(server.queue)))

    def arrivals(env, server):
        while True:
            yield env.timeout(rng.exponential(1.0 / lam))
            env.process(customer(env, server))

    env.process(arrivals(env, server))
    env.run(until=sim_time)

    n_served = len(wait_times)
    rho_obs = busy_time / sim_time if sim_time > 0 else 0

    return {
        "rho": rho_obs,
        "mean_wait": float(np.mean(wait_times))   if wait_times else 0.0,
        "mean_system": float(np.mean(wait_times)) + (1.0 / mu) if wait_times else 0.0,
        "wait_times": wait_times,
        "queue_log": queue_log,
        "n_served": n_served,
    }

