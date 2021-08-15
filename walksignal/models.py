import numpy as np
from scipy import special as sp
from scipy import constants
from dataclasses import dataclass

def pl_fs(dist, freq):
    return 20 * np.log10(dist) + 20 * np.log10(freq) - 27.55

def pl_oh_corr_factor(ue_height, freq, large_city=True):
    if (large_city == True):
        if (freq < 300):
            return 8.29 * np.square(np.log10(1.54 * ue_height)) - 1.1
        else:
            return 3.2 * np.square(np.log10(11.75 * ue_height)) - 4.97
    else:
        return (1.1 * np.log10(freq) - 0.7) * ue_height - (1.56 * np.log10(freq) - 0.8)

def pl_oh_urban(dist, freq, bs_height, ue_height, large_city=True):
    return 69.55 + 26.26 * np.log10(freq) + (44.9 - 6.55 * np.log10(bs_height)) * np.log10(dist / 1000) - 13.85 * np.log10(bs_height) - pl_oh_corr_factor(ue_height, freq, large_city)

def pl_oh_suburban(dist, freq, bs_height, ue_height, large_city=False):
    return pl_oh_urban(dist, freq, bs_height, ue_height, large_city) - 2 * np.square(np.log10(freq / 28)) - 5.4

def pl_oh_rural(dist, freq, bs_height, ue_height, large_city=False):
    return pl_oh_urban(dist, freq, bs_height, ue_height, large_city) - 4.78 * np.square(np.log10(freq)) + 18.33 * np.log10(freq) - 40.94

def pl_abg(dist, freq, alpha, beta, gamma, sigma, ref_dist=1, ref_freq=1000000000):
    return 10 * alpha * np.log10(dist/ref_dist) + beta + 10 * gamma * np.log10(freq/ref_freq) + np.random.normal(0, sigma)

def v_pl_abg(array, freq, alpha, beta, gamma, sigma, ref_dist=1, ref_freq=1000000000):
    return np.array([pl_abg(xi, freq, alpha, beta, gamma, sigma, ref_dist, ref_freq) for xi in array])
    
def pl_ci(dist, freq, sigma, pl_exp, ref_dist=1):
    return pl_fs(ref_dist, freq) + 10 * pl_exp * np.log10(dist/ref_dist) + np.random.normal(0, sigma)

def v_pl_ci(array, freq, sigma, pl_exp, ref_dist=1):
    return np.array([pl_ci(xi, freq, sigma, pl_exp, ref_dist) for xi in array])

def v_pl_fs(array, freq):
    return np.array([pl_fs(xi, freq) for xi in array])

def v_pl_oh_urban(array, freq, bs_height, ue_height, large_city=True):
    return np.array([pl_oh_urban(xi, freq, bs_height, ue_height, large_city) for xi in array])

def v_pl_oh_suburban(array, freq, bs_height, ue_height, large_city=False):
    return np.array([pl_oh_suburban(xi, freq, bs_height, ue_height, large_city) for xi in array])

def v_pl_oh_rural(array, freq, bs_height, ue_height, large_city=False):
    return np.array([pl_oh_rural(xi, freq, bs_height, ue_height, large_city) for xi in array])

@dataclass
class FreeSpaceModel:
    """Class representing the free space path loss model for
    line-of-sight communications."""
    freq: float

    def path_loss(self, dist):
        return 20 * np.log10(dist) + 20 * np.log10(self.freq) - 27.55

    def v_path_loss(self, array):
        return np.array([self.path_loss(xi, self.freq) for xi in array])

@dataclass
class ABGModel(FreeSpaceModel):
    """Class representing the Alpha-Beta-Gamma path loss model for
    line-of-sight communications."""
    alpha: float
    beta: float
    gamma: float
    sigma: float
    ref_dist: float = 1
    ref_freq: float = 1000000000

    def path_loss(self, dist):
        return 10 * self.alpha * np.log10(dist/self.ref_dist) + self.beta + 10 * self.gamma * np.log10(self.freq/self.ref_freq) + np.random.normal(0, self.sigma)

    def v_path_loss(self, array):
        return np.array([self.path_loss(xi, self.freq, self.alpha, self.beta, self.gamma, self.sigma, self.ref_dist, self.ref_freq) for xi in array])

@dataclass
class CIModel(FreeSpaceModel):
    """Class representing the Close-In path loss model for line-of-sight
    communications."""
    freq: float
    pl_exp: float
    sigma: float
    ref_dist: float = 1

    def path_loss(self, dist):
        return super().path_loss(self.ref_dist, self.freq) + 10 * self.pl_exp * np.log10(dist/self.ref_dist) + np.random.normal(0, self.sigma)

    def v_path_loss(self, array):
        return np.array([self.path_loss(xi, self.freq, self.sigma, self.pl_exp, self.ref_dist) for xi in array])

@dataclass
class OHUrbanModel:
    """Class representing the Okumura-Hata urban propagation model."""
    freq: float
    bs_height: float
    ue_height: float
    large_city: bool = True

    def corr_factor(self):
        if self.large_city:
            if self.freq < 300:
                return 8.29 * np.square(np.log10(1.54 * self.ue_height)) - 1.1
            else:
                return 3.2 * np.square(np.log10(11.75 * self.ue_height)) - 4.97
        else:
            return (1.1 * np.log10(self.freq) - 0.7) * self.ue_height - (1.56 * np.log10(self.freq) - 0.8)

    def path_loss(self, dist):
        return 69.55 + 26.26 * np.log10(dist) + (44.9 - 6.55 * np.log10(self.bs_height)) * np.log10(dist / 1000) - 13.65 * np.log10(self.bs_height) - self.corr_factor(self.ue_height, self.freq, self.large_city)

    def v_path_loss(self, array):
        return np.array([self.path_loss(xi, self.freq, self.bs_height, self.ue_height, self.large_city) for xi in array])

@dataclass
class OHSuburbanModel(OHUrbanModel):
    """Class representing the Okumura-Hata suburban propagation model."""

    def path_loss(self, dist):
        return super().path_loss(dist, self.freq, self.bs_height, self.ue_height, self.large_city) - 2 * np.square(np.log10(self.freq / 28)) - 5.4

    def v_path_loss(self, array):
        return super().v_path_loss(array)

@dataclass
class OHRuralModel(OHUrbanModel):
    """Class representing the Okumura-Hata rural propagation model."""

    def path_loss(self, dist):
        return super().path_loss(dist, self.freq, self.bs_height, self.ue_height, self.large_city) - 4.78 * np.square(np.log10(self.freq)) + 18.33 * np.log10(self.freq) - 40.94

    def v_path_loss(self, array):
        return super().v_path_loss(array)
