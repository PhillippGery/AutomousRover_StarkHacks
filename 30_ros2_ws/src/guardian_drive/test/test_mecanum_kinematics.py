# MIT License
# GUARDIAN — StarkHacks 2026
# Test: test_mecanum_kinematics
# Owner: Phillipp
# Purpose: unit tests for mecanum kinematics math

import unittest
import math


class TestMecanumKinematics(unittest.TestCase):
    """Unit tests for mecanum wheel kinematics equations."""

    def setUp(self):
        self.wheel_radius = 0.048  # meters
        self.L = 0.25 / 2.0       # half wheel-base length
        self.W = 0.20 / 2.0       # half wheel-base width

    def compute_rpms(self, vx, vy, omega):
        """Compute wheel RPMs from desired robot velocity."""
        r = self.wheel_radius
        L = self.L
        W = self.W
        fl = (vx - vy - (L + W) * omega) / r * 60.0 / (2.0 * math.pi)
        fr = (vx + vy + (L + W) * omega) / r * 60.0 / (2.0 * math.pi)
        bl = (vx + vy - (L + W) * omega) / r * 60.0 / (2.0 * math.pi)
        br = (vx - vy + (L + W) * omega) / r * 60.0 / (2.0 * math.pi)
        return fl, fr, bl, br

    # TODO: implement real tests once node is implemented
    def test_forward_motion_all_wheels_equal(self):
        """Pure forward motion: all four wheels should spin at the same RPM."""
        # TODO: uncomment and verify once kinematics are implemented
        pass

    def test_strafe_motion(self):
        """Pure lateral (strafe) motion: FL/BR reverse, FR/BL forward."""
        # TODO: uncomment and verify once kinematics are implemented
        pass

    def test_zero_velocity(self):
        """Zero command: all RPMs should be zero."""
        fl, fr, bl, br = self.compute_rpms(0.0, 0.0, 0.0)
        self.assertAlmostEqual(fl, 0.0)
        self.assertAlmostEqual(fr, 0.0)
        self.assertAlmostEqual(bl, 0.0)
        self.assertAlmostEqual(br, 0.0)


if __name__ == '__main__':
    unittest.main()
