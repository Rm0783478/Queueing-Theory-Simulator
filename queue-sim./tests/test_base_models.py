"""
Tests: these verify simulated output matches theoretical values within tolerance.

Run with: python -m pyset tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sim import mm1, mmk, mg1

# Tolerance: 10% (similated values should be within 10% of the theoretical ones)
RTOL = 0.10

def within(simulated: float, theoretical: float, rtol: float = RTOL) -> bool:
    if theoretical == 0:
        return abs(simulated) < 1e-6
    return abs(simulated - theoretical) / theoretical <= rtol

# M/M/1 TEST
class TestMM1:
    lam, mu = 0.8, 1.0 # rho = 0.8

    def test_util(self):
        result = mm1.run(self.lam, self.mu, sim_time = 20000, seed = 0)
        theory = mm1.theoretical(self.lam, self.mu)
        assert within(result["rho"], theory["rho"]), (
            f"rho: sim = {result['rho']:.3f}, theory = {theory['rho']:.3f}"
        )
    
    def test_mean_wait(self):
        # High rho (0.8) queues have high varuance anduse longer run and wider tolerance
        result = mm1.run(self.lam, self.mu, sim_time = 100000, seed = 0)
        theory = mm1.theoretical(self.lam, self.mu)
        assert within(result["rho"], theory["rho"]), (
            f"rho: sim = {result['rho']:.3f}, theory = {theory['rho']:.3f}"
        )

    def test_unstable_queue(self):
        """rho >= 1 should return inf theoretical values."""
        theory = mm1.theoretical(lam=1.5, mu=1.0)
        assert theory["Wq"] == float("inf")
    
    def test_returns_wait_times(self):
        result = mm1.run(self.lam, self.mu, sim_time=1000, seed=0)
        assert len(result["wait_times"]) > 0
    
    def test_returns_wait_times(self):
        result = mm1.run(self.lam, self.mu, sim_time=1000, seed=0)
        assert len(result["wait_times"]) > 0

# M/M/k TEST
class TestMMK:
    lam, mu, k = 1.6, 1.0, 2 # rho per server = 0.8

    def test_utilization(self):
        result = mmk.run(self.lam, self.mu, k=self.k, sim_time=20000, seed=0)
        theory = mmk.theoretical(self.lam, self.mu, self.k)
        assert within(result["rho"], theory["rho"]), (
            f"rho: sim={result['rho']:.3f}, theory={theory['rho']:.3f}"
        )

    def test_mean_wait(self):
        result = mmk.run(self.lam, self.mu, k=self.k, sim_time=100000, seed=0)
        theory = mmk.theoretical(self.lam, self.mu, self.k)
        assert within(result["mean_wait"], theory["Wq"], rtol=0.15), (
            f"Wq: sim={result['mean_wait']:.3f}, theory={theory['Wq']:.3f}"
        )

    def test_mmk_better_than_mm1(self):
        """Adding a second server should reduce wait time."""
        r1 = mm1.run(lam = 0.8, mu = 1.0, sim_time = 10000, seed = 1)
        rk = mmk.run(lam = 1.6, mu = 1.0, k = 2, sim_time = 10000, seed = 1)
        # M/M/2 at same total load should have lower per-customer wait than M/M/1
        assert rk["mean_wait"] < r1["mean_wait"]

# M/G/1 TEST
class TestMG1:
    lam, mu = 0.8, 1.0

    @pytest.mark.parametrize("dist_cv", [
        ("exponential", 1.0),
        ("normal", 0.5),
        ("lognormal", 1.5),
        ("uniform", 0.5),
    ])
    def test_mean_wait(self, dist, cv):
        result = mg1.run(self.lam, self.mu, dist=dist, cv=cv, sim_time=20000, seed=0)
        theory = mg1.theoretical(self.lam, self.mu, cv=cv)
        assert within(result["mean_wait"], theory["Wq"], rtol=0.15), (
            f"[{dist}] Wq: sim={result['mean_wait']:.3f}, theory={theory['Wq']:.3f}"
        )
    
    def test_higher_cv_higher_wait(self):
        """Higher service time variance means longer wait (per P-K formula)."""
        r_low = mg1.run(self.lam, self.mu, dist = "lognormal", cv = 0.5, sim_time = 20000, seed = 0)
        r_high = mg1.run(self.lam, self.mu, dist = "lognormal", cv = 2.0, sim_time = 20000, seed = 0)
        assert r_high["mean_wait"] > r_low["mean_wait"]