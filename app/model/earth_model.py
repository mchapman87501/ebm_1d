#!/usr/bin/env python3
"""
Define geometry/insolation of earth in terms of latitude bands.
"""

import typing as tp

import numpy as np


class EarthModel:
    def __init__(self, num_zones: int) -> None:
        assert num_zones > 0

        # Clients should treat all attributes as read-only.
        self.num_zones = num_zones
        self.delta_rad, self.lats_rad = self._get_lat_bands(self.num_zones)
        self.lats_height = self._get_band_heights(
            self.lats_rad, self.delta_rad
        )
        self.lats_frac = self._get_normed_areas(
            self.lats_rad, self.lats_height
        )
        self.insol_by_lat = self._get_insol_by_lat(self.lats_frac)

    @staticmethod
    def _get_lat_bands(num_zones: int) -> tp.Tuple[float, np.ndarray]:
        d2r = np.pi / 180.0
        zone_width_deg = 90.0 / num_zones
        zw2 = d2r * zone_width_deg / 2.0
        # Central angle of each latitude band, radians, for
        # one hemisphere:
        lat_rads = np.arange(zw2, np.pi / 2.0, zw2 * 2.0)
        # Return 1/2 of the latitude band, and the band central angles.
        return (zw2, lat_rads)

    @staticmethod
    def _get_band_heights(
        lats_rad: np.ndarray, delta_rad: float
    ) -> np.ndarray:
        # Treat earth as a stack of cylinders.  The radius of each
        # cylinder corresponds to the (unit) radius of the earth
        # sphere at the central latitude of each band.
        return np.sin(lats_rad + delta_rad) - np.sin(lats_rad - delta_rad)

    @staticmethod
    def _get_normed_areas(
        lats_rad: np.ndarray, lats_height: np.ndarray
    ) -> np.ndarray:
        # Get normalized (fractional) areas of latitude bands.
        lats_radius = np.cos(lats_rad)
        lats_area = lats_radius * lats_height

        total_area = sum(lats_area)
        return lats_area / total_area

    @staticmethod
    def _get_insol_by_lat(lats_frac: np.ndarray) -> np.ndarray:
        S = 1370.0  # Solar constant, watts / m**2

        # Ratio of cross-sectional area of a sphere to surface area of
        # a sphere is (π * r**2) / (4 * π * r**2)
        solar_constant = S / 4.0

        # Assume axial tilt relative to orbital plane averages to zero
        # over the course of a year.
        return solar_constant * lats_frac
