import numpy as np
from scipy import special as sp
from scipy import constants
from dataclasses import dataclass

@dataclass
class FreeSpaceModel:
    """Class representing the free space path loss model for
    line-of-sight communications. Distance is in meters, frequency is in MHz."""
    freq: float

    def path_loss(self, dist):
        return 20 * np.log10(dist) + 20 * np.log10(self.freq) - 27.55

    def path_loss_array(self, array):
        return np.array([self.path_loss(xi) for xi in array])

@dataclass
class TwoRayModel:
    """Class representing the two-ray path loss model for line-of-sight
    communications. This version of the model does not explicitly
    require frequency, instead relying on the empirically-determined nu. ref_pl
    is in dB, ref_dist is in meters."""
    ref_pl: float
    pl_exp: float
    ref_dist: float

    def path_loss(self, dist):
        return self.ref_pl + 10 * self.pl_exp * np.log10(dist/self.ref_dist)

    def path_loss_array(self, array):
        return np.array([self.path_loss(xi) for xi in array])

@dataclass
class MultiSlopeModel:
    """Class representing the Multi-Slope Propagation Model which consists
    of the Free Space Model below the critical distance, and the Two-Ray
    Multipath propagation model above it. freq is in Mhz, bs_height and
    ue_height are in meters."""
    freq: float
    bs_height: float
    ue_height: float

    def crit_dist(self):
        return (4 * constants.pi * self.ue_height * self.bs_height * self.freq) / constants.speed_of_light

    def path_loss(self, dist):
        if dist < self.crit_dist():
            # Free space model below this distance
            return 20 * np.log10(dist) + 20 * np.log10(self.freq) - 27.55
        else:
            # Two-Ray Multipath Model
            return 40 * np.log10(dist) - 20 * np.log10(self.bs_height * self.ue_height)

    def path_loss_array(self, array):
        return np.array([self.path_loss(xi) for xi in array])

@dataclass
class ABGModel(FreeSpaceModel):
    """Class representing the Alpha-Beta-Gamma path loss model for
    line-of-sight communications. Assumes that distance is measured in
    meters, frequency in MHz."""
    alpha: float
    beta: float
    gamma: float
    sigma: float
    ref_dist: float = 1

    def path_loss(self, dist):
        return 10 * self.alpha * np.log10(dist/self.ref_dist) + self.beta + 10 * self.gamma * np.log10(self.freq/1000) + np.random.normal(0, self.sigma)

    def path_loss_array(self, array):
        return np.array([self.path_loss(xi) for xi in array])

@dataclass
class CIModel(FreeSpaceModel):
    """Class representing the Close-In path loss model for line-of-sight
    communications. Assumes distance in meters, frequency in MHz"""
    freq: float
    pl_exp: float
    sigma: float
    ref_dist: float = 1

    def path_loss(self, dist):
        return super().path_loss(self.ref_dist) + 10 * self.pl_exp * np.log10(dist/self.ref_dist) + np.random.normal(0, self.sigma)

    def path_loss_array(self, array):
        return np.array([self.path_loss(xi) for xi in array])

@dataclass
class OHUrbanModel:
    """Class representing the Okumura-Hata urban propagation model. Assumes
    distance and heights in meters, frequency in MHz."""
    freq: float
    bs_height: float
    ue_height: float
    large_city: bool = True

    def large_city_correction_factor(self):
        if self.freq < 300:
            return 8.29 * np.square(np.log10(1.54 * self.ue_height)) - 1.1
        else:
            return 3.2 * np.square(np.log10(11.75 * self.ue_height)) - 4.97

    def small_city_correction_factor(self):
        return (1.1 * np.log10(self.freq) - 0.7) * self.ue_height - (1.56 * np.log10(self.freq) - 0.8)

    def base_path_loss(self, dist):
        return 69.55 + 26.26 * np.log10(self.freq) + (44.9 - 6.55 * np.log10(self.bs_height)) * np.log10(dist / 1000) - 13.85 * np.log10(self.bs_height)

    def path_loss(self, dist):
        if self.large_city:
            return self.base_path_loss(dist) - self.large_city_correction_factor()
        else:
            return self.base_path_loss(dist) - self.small_city_correction_factor()

    def path_loss_array(self, array):
        return np.array([self.path_loss(xi) for xi in array])

@dataclass
class OHSuburbanModel(OHUrbanModel):
    """Class representing the Okumura-Hata suburban propagation model. Assumes
    distance and heights in meters, frequency in MHz."""

    def path_loss(self, dist):
        return super().base_path_loss(dist) - super().small_city_correction_factor() - 2 * np.square(np.log10(self.freq / 28)) - 5.4

    def path_loss_array(self, array):
        return super().path_loss_array(array)

@dataclass
class OHRuralModel(OHUrbanModel):
    """Class representing the Okumura-Hata rural propagation model. Assumes
    distance and heights in meters, frequency in MHz."""

    def path_loss(self, dist):
        return super().base_path_loss(dist) - super().small_city_correction_factor() - 4.78 * np.square(np.log10(self.freq)) + 18.33 * np.log10(self.freq) - 40.94

    def path_loss_array(self, array):
        return super().path_loss_array(array)

