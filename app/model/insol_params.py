#!/usr/bin/env python3
"""
Provides parameters for simple insolation calculations.
"""

from dataclasses import dataclass


@dataclass
class InsolParams:
    solar_const: float = 1370  # Solar constant, watts / m**2
    max_tilt: float = 23.5  # Deg tilt of earth's rot axis wrt ecliptic normal

    # Gee, compared to the calculations in NASA's solar irradiation code
    # this is way over-simplified
    days_in_yr: float = 365.0
    hrs_in_day: float = 24.0
    zonal_deg: float = 360.0  # *longitude* zones, not lat zones.
