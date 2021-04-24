import numpy as np
from scipy import special as sp
from scipy import constants

# Equation 12 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd2d(obs_dens, absorption, x_range):
    external_multiplier = obs_dens * absorption / (2 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    bessel = internal_multiplier * sp.kv(0, exp_mult_1 * x_range)
    first_component = internal_multiplier * np.multiply(x_range, bessel)
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y

# Equation 12 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd3d(obs_dens, absorption, x_range):
    external_multiplier = obs_dens * absorption / (4 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    first_component = internal_multiplier * np.multiply(x_range, np.exp(-1 * exp_mult_1 * x_range))
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y

def pl_fs(distance, frequency):
    return 20 * np.log10(4 * constants.pi * distance * frequency / constants.speed_of_light)

def pl_los_5gcm_ci(distance, frequency):
    return 32.4 + 20 * np.log10(distance) + 20 * np.log10(frequency)

def pl_nlos_5gcm_ci(distance, frequency):
    return 32.4 + 30 * np.log10(distance) + 20 * np.log10(frequency)

def pl_nlos_5gcm_abg(distance, frequency):
    return 19.2 + 34 * np.log10(distance) + 23 * np.log10(frequency)

def v_pl_fs(array, frequency):
    return np.array([pl_fs(xi, frequency) for xi in array])

def v_pl_los_5gcm_ci(array, frequency):
    return np.array([pl_los_5gcm_ci(xi, frequency) for xi in array])

def v_pl_nlos_5gcm_ci(array, frequency):
    return np.array([pl_nlos_5gcm_ci(xi, frequency) for xi in array])

def v_pl_nlos_5gcm_abg(distance, frequency):
    return np.array([pl_nlos_5gcm_abg(xi, frequency) for xi in array])

