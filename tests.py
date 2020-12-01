from numpy.testing import assert_equal
from src.baselines import baseline_season, baseline_yesterday
import numpy as np

day_len = 4
demand = np.hstack([
    np.full(day_len, 2),
    np.full(day_len, 4),
    np.full(day_len, 7),
    np.full(day_len, 1)
])
expected_errors = [-2.0, -3.0, 6.0]
pred, target, errors = baseline_yesterday(demand, day_len)
assert_equal(errors, expected_errors)

_, _, errors = baseline_season(demand, day_len, season_len=1)
assert_equal(errors, expected_errors)

day_len = 7
season_len = 3
demand = np.hstack([
    np.full(day_len, 1),
    np.full(day_len, 3),
    np.full(day_len, 6),
    np.full(day_len, 10),
    np.full(day_len, 15),
    np.full(day_len, -21),
    np.full(day_len, -28),
])

expected_errors = [-9, -12, 27, 38]
_, _, errors = baseline_season(demand, day_len, season_len)
assert_equal(errors, expected_errors)
