import unittest

import numpy as np

from drosophila_pd_flygym import DrosophilaPDSimulation, SimulationConfig


class _FakeBackend:
    def __init__(self) -> None:
        self.last_drive = None
        self.last_timestep = None

    def run(self, *, drive_signal, timestep_s):
        self.last_drive = drive_signal
        self.last_timestep = timestep_s
        return {"ok": True, "steps": drive_signal.shape[0]}


class SimulationTests(unittest.TestCase):
    def test_config_validation(self):
        with self.assertRaises(ValueError):
            SimulationConfig(duration_s=0)
        with self.assertRaises(ValueError):
            SimulationConfig(pd_severity=1.5)

    def test_pd_reduces_speed_proxy(self):
        healthy = DrosophilaPDSimulation(SimulationConfig(pd_severity=0.0)).run()
        pd = DrosophilaPDSimulation(SimulationConfig(pd_severity=1.0)).run()

        self.assertLess(pd["speed_proxy"], healthy["speed_proxy"])
        self.assertGreater(pd["asymmetry"], healthy["asymmetry"])

    def test_backend_path(self):
        backend = _FakeBackend()
        config = SimulationConfig(duration_s=0.1, timestep_s=0.01, pd_severity=0.5)
        result = DrosophilaPDSimulation(config, backend=backend).run()

        self.assertTrue(result["ok"])
        self.assertEqual(result["steps"], 10)
        self.assertIsNotNone(backend.last_drive)
        self.assertEqual(backend.last_timestep, config.timestep_s)


if __name__ == "__main__":
    unittest.main()
