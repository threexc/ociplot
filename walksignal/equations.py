import numpy as np
from scipy import special as sp
from scipy import constants

# Equation 13 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd2d(obs_dens, absorption, x_range, gain_factor=1):
    external_multiplier = obs_dens * absorption / (2 * np.pi * x_range)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    bessel = internal_multiplier * sp.kv(0, exp_mult_1 * x_range)
    first_component = internal_multiplier * np.multiply(x_range, bessel)
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y * gain_factor

# Equation 13 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd3d(obs_dens, absorption, x_range, gain_factor=1):
    external_multiplier = obs_dens * absorption / (4 * np.pi * x_range * x_range)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    first_component = internal_multiplier * np.multiply(x_range, np.exp(-1 * exp_mult_1 * x_range))
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y * gain_factor

def pl_fs(dist, freq):
    return 20 * np.log10(dist) + 20 * np.log10(freq) - 27.55

def pl_los_5gcm_ci(dist, freq):
    return 32.4 + 20 * np.log10(dist) + 20 * np.log10(freq)

def pl_nlos_5gcm_ci(dist, freq):
    return 32.4 + 30 * np.log10(dist) + 20 * np.log10(freq)

def pl_nlos_5gcm_abg(dist, freq):
    return 19.2 + 34 * np.log10(dist) + 23 * np.log10(freq)

def v_pl_los_5gcm_ci(array, freq):
    return np.array([pl_los_5gcm_ci(xi, freq) for xi in array])

def v_pl_nlos_5gcm_ci(array, freq):
    return np.array([pl_nlos_5gcm_ci(xi, freq) for xi in array])

def v_pl_nlos_5gcm_abg(dist, freq):
    return np.array([pl_nlos_5gcm_abg(xi, freq) for xi in array])

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

def v_pl_oh_urban(array, freq, bs_height, ue_height, large_city=True):
    return np.array([pl_oh_urban(xi, freq, bs_height, ue_height, large_city) for xi in array])

def v_pl_oh_suburban(array, freq, bs_height, ue_height, large_city=False):
    return np.array([pl_oh_suburban(xi, freq, bs_height, ue_height, large_city) for xi in array])

def v_pl_oh_rural(array, freq, bs_height, ue_height, large_city=False):
    return np.array([pl_oh_rural(xi, freq, bs_height, ue_height, large_city) for xi in array])
