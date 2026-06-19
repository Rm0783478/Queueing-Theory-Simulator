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