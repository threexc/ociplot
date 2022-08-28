import numpy as np
from scipy import special as sp
from scipy import constants

class ModelEngine:
    """ModelEngine provides methods for calculating path loss (or path gain) based
    on various popular wireless propagation models. ModelEngine itself requires a
    single input, a "config" object that contains values for the variables used by
    each method. All public methods return loss/gain and sigma values in dB, while
    taking distances and heights in meters, frequency in MHz, and any other values
    as unitless. Methods with the _array suffix calculate path loss over an entire
    range of distances."""
    def __init__(self, config):
        self.config = config

    def fs_pl(self, dist):
        """Calculate the free space path loss at a given distance."""
        return 20 * np.log10(dist) + 20 * np.log10(self.config.freq) - 27.55 - self.config.tx_gain - self.config.rx_gain

    def tworay_pl(self, dist):
        """Calculate the Two-Ray model path loss at a given distance, using the
        height of the base station and the user equipment."""
        return 40 * np.log10(dist) - 10 * np.log10(np.power(self.config.bs_height, 2) * np.power(self.config.ue_height,2)) - self.config.tx_gain - self.config.rx_gain
    
    def abg_pl(self, dist):
        """Calculate the Alpha-Beta-Gamma model path loss at a given
        distance."""
        return 10 * self.config.alpha * np.log10(dist/self.config.ref_dist) + self.config.beta + 10 * self.config.gamma * np.log10(self.config.freq/1000) - self.config.tx_gain - self.config.rx_gain

    def ci_pl(self, dist):
        """Calculate the Close-In model path loss at a given distance."""
        return self.fs_pl(self.config.ref_dist) + 10 * self.config.pl_exp * np.log10(dist/self.config.ref_dist) - self.config.tx_gain - self.config.rx_gain

    def ohu_pl(self, dist):
        """Calculate the Okumura-Hata Urban model path loss at a given
        distance."""
        if self.config.large_city:
            return self._base_path_loss(dist) - self._large_city_correction_factor() - self.config.tx_gain - self.config.rx_gain
        else:
            return self._base_path_loss(dist) - self._small_city_correction_factor() - self.config.tx_gain - self.config.rx_gain

    def ohs_pl(self, dist):
        """Calculate the Okumura-Hata Suburban model path loss at a given
        distance."""
        return self.ohu_pl(dist) - 2 * np.square(np.log10(self.config.freq / 28)) - 5.4

    def ohr_pl(self, dist):
        """Calculate the Okumura-Hata Rural model path loss at a given
        distance."""
        return self.ohu_pl(dist) - 4.78 * np.square(np.log10(self.config.freq)) + 18.33 * np.log10(self.config.freq) - 40.94

    def _large_city_correction_factor(self):
        if self.config.freq < 300:
            return 8.29 * np.square(np.log10(1.54 * self.config.ue_height)) - 1.1
        else:
            return 3.2 * np.square(np.log10(11.75 * self.config.ue_height)) - 4.97

    def _small_city_correction_factor(self):
        return (1.1 * np.log10(self.config.freq) - 0.7) * self.config.ue_height - (1.56 * np.log10(self.config.freq) - 0.8)

    def _base_path_loss(self, dist):
        return 69.55 + 26.26 * np.log10(self.config.freq) + (44.9 - 6.55 * np.log10(self.config.bs_height)) * np.log10(dist / 1000) - 13.85 * np.log10(self.config.bs_height)

    def fs_pl_array(self, x_range):
        return np.array([self.fs_pl(xi) for xi in x_range])

    def tworay_pl_array(self, x_range):
        return np.array([self.tworay_pl(xi) for xi in x_range])

    def abg_pl_array(self, x_range):
        random_val = np.random.normal(0, self.config.sigma)
        random_array = []

        for i in range(0, len(x_range)):
            if (i+1) % int(self.config.coherence_length) == 0:
                f"{i+1} == {self.config.coherence_length}"
                random_val = np.random.normal(0, self.config.sigma)
            random_array.append(random_val)

        return np.array([self.abg_pl(xi) + random_array[index] for index, xi in enumerate(x_range)])

    def ci_pl_array(self, x_range):
        random_val = np.random.normal(0, self.config.sigma)
        random_array = []

        for i in range(0, len(x_range)):
            if (i+1) % int(self.config.coherence_length) == 0:
                random_val = np.random.normal(0, self.config.sigma)
            random_array.append(random_val)

        return np.array([self.ci_pl(xi) + random_array[index] for index, xi in enumerate(x_range)])

    def ohu_pl_array(self, x_range):
        return np.array([self.ohu_pl(xi) for xi in x_range])

    def ohs_pl_array(self, x_range):
        return np.array([self.ohs_pl(xi) for xi in x_range])

    def ohr_pl_array(self, x_range):
        return np.array([self.ohr_pl(xi) for xi in x_range])

    def fs_pg_array(self, x_range):
        return np.array([self.fs_pl(xi) * -1 for xi in x_range])

    def tworay_pg_array(self, x_range):
        return np.array([self.tworay_pl(xi) * -1 for xi in x_range])

    def abg_pg_array(self, x_range):
        random_val = np.random.normal(0, self.config.sigma)
        random_array = []

        for i in range(0, len(x_range)):
            if (i+1) % int(self.config.coherence_length) == 0:
                random_val = np.random.normal(0, self.config.sigma)
            random_array.append(random_val)

        return np.array([(self.abg_pl(xi) + random_array[index]) * -1 for index, xi in enumerate(x_range)])

    def ci_pg_array(self, x_range):
        random_val = np.random.normal(0, self.config.sigma)
        random_array = []

        for i in range(0, len(x_range)):
            if (i+1) % int(self.config.coherence_length) == 0:
                random_val = np.random.normal(0, self.config.sigma)
            random_array.append(random_val)

        return np.array([(self.ci_pl(xi) + random_array[index]) * -1 for index, xi in enumerate(x_range)])

    def ohu_pg_array(self, x_range):
        return np.array([self.ohu_pl(xi) * -1 for xi in x_range])

    def ohs_pg_array(self, x_range):
        return np.array([self.ohs_pl(xi) * -1 for xi in x_range])

    def ohr_pg_array(self, x_range):
        return np.array([self.ohr_pl(xi) * -1 for xi in x_range])
