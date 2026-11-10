import unittest
from tools.watchface_device_check import validate_trials, validate_calibration

BASE = [(131, 226), (320, 226)]


def sample(seconds, eyes):
    return {'seconds': seconds, 'eyes': eyes}


def orbit():
    # Hand-constructed clockwise left / counterclockwise right orbit, radius26 below neutral gaze.
    return [sample(.3, [(157, 252), (294, 252)]),
            sample(.8, [(131, 278), (320, 278)]),
            sample(1.4, [(105, 252), (346, 252)]),
            sample(2.1, [(118, 229), (333, 229)]),
            sample(3.8, BASE), sample(4.43, BASE), sample(5.17, BASE)]


class DeviceEvidenceTest(unittest.TestCase):
    def test_accepts_opposite_orbits_then_stationary_recovery(self):
        validate_trials(BASE, [orbit(), orbit()])

    def test_rejects_a_brief_twitch_that_stops_before_one_second(self):
        short = [orbit()[0], *[sample(t, BASE) for t in (.8, 1.4, 2.1, 3.8, 4.43, 5.17)]]
        with self.assertRaises(AssertionError):
            validate_trials(BASE, [short])

    def test_rejects_continuous_motion_crossing_baseline_at_one_sample(self):
        continuous = orbit()
        continuous[-2] = sample(4.43, [(157, 252), (294, 252)])
        with self.assertRaises(AssertionError):
            validate_trials(BASE, [continuous])

    def test_rejects_reversed_orbital_directions(self):
        reversed_frames = [sample(f['seconds'], [(2 * BASE[i][0] - x, y) for i, (x, y) in enumerate(f['eyes'])]) for f in orbit()]
        with self.assertRaises(AssertionError):
            validate_trials(BASE, [reversed_frames])

    def test_rejects_injection_that_never_reaches_pupils(self):
        with self.assertRaises(RuntimeError):
            validate_calibration(BASE, BASE, BASE)

    def test_accepts_same_direction_tilt_and_recovery(self):
        validate_calibration(BASE, [(151, 226), (340, 226)], BASE)
