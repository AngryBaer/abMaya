
# ----------------------------------------------------------------------------------------------- #
# IMPORTS
from math import pow, sqrt
from scipy.stats import norm
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
# True constrast operation that preserves minimum and maximum values.
def contrast(value, weight, vtx_min, vtx_max):
    norm_range = vtx_max - vtx_min                                               # find normal range
    difference = weight - ((vtx_max + vtx_min) / 2)                              # vtx_weight - min/max average
    multiplier = norm.cdf(difference, loc=0, scale=(0.1 * norm_range)) - weight  # apply normal random variable
    return max(vtx_min, min(weight + (value * multiplier) , vtx_max))            # clamp output to min/max
# ----------------------------------------------------------------------------------------------- #
