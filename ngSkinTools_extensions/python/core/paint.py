
# ----------------------------------------------------------------------------------------------- #
# IMPORTS
from math import pow, sqrt
from scipy.stats import norm
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
# True constrast operation that preserves minimum and maximum values.
def contrast(value, weight, vtxMin, vtxMax):
    """ sharpen edge of active weight map on brushstroke """
    norm_range = vtxMax - vtxMin                                                 # find range of normal variable operation
    difference = weight - ((vtxMax + vtxMin) / 2.0)                              # find difference between current weight and average
    multiplier = norm.cdf(difference, loc=0, scale=(0.1 * norm_range)) - weight  # apply normal random variable
    return max(vtxMin, min(weight + (value * multiplier) , vtxMax))              # clamp output to min/max
# ----------------------------------------------------------------------------------------------- #
