#!/usr/bin/env python3
"""
Define geometry of earth as a sequence of latitude bands.
"""

import numpy as np


class EarthGeom:
    def __init__(self, num_zones: int) -> None:
        assert num_zones > 0

        # Clients should treat all attributes as read-only.
        self.num_zones = num_zones
        zone_width_deg = 90.0 / num_zones
        # Midpoint latitudes in degrees:
        zw2 = zone_width_deg / 2.0

        # Central angle of each latitude band, degrees, for
        # one hemisphere:
        lat_degs = np.arange(zw2, 90.0, zone_width_deg)

        # Ditto, radians:
        self.lats_rad = lat_degs * np.pi / 180.0
        # One half of the width of each zone, in rads:
        delta_rad = zw2 * np.pi / 180.0

        # Treat earth as a stack of cylinders.  The radius of each
        # cylinder corresponds to the (unit) radius of the earth
        # sphere at the central latitude of each band.
        lats_radius = np.cos(self.lats_rad)
        self.lats_height = np.sin(self.lats_rad + delta_rad) - np.sin(
            self.lats_rad - delta_rad
        )
        lats_area = lats_radius * self.lats_height  # * 2.0 * np.pi

        total_area = sum(lats_area)
        self.lats_frac = lats_area / total_area
        self.delta_rad = delta_rad
