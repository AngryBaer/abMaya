
# IMPORTS --------------------------------------------------------------------------------------- #
from math import pow, sqrt
from scipy.stats import norm
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
def contrast(value, weight, vtxMin, vtxMax):
    """
    True contrast operation that preserves minimum and maximum values.
    Applies a curve to the given weight value that increases its distance to the average value.

    :param value:   intensity value of the brush stroke
                     - float 0.0 - 1.0
    :param weight:  current weight value of the given vertex
                     - float 0.0 - 1.0
    :param vtxMin:  minimum weight value of affected vertices
                     - float 0.0 - 1.0
    :param vtxMax:  maximum weight vlaue of affected vertices
                     - float 0.0 - 1.0

    :return result: modified weight value
                     - float 0.0 - 1.0
    """
    norm_range = vtxMax - vtxMin                                                 # find range of normal variable operation
    difference = weight - ((vtxMax + vtxMin) / 2.0)                              # find difference between current weight and average
    multiplier = norm.cdf(difference, loc=0, scale=(0.1 * norm_range)) - weight  # apply normal random variable
    return max(vtxMin, min(weight + (value * multiplier) , vtxMax))              # clamp output to min/max


def gain(value, weight):
    """
    Gain operation that preserves zero weights.
    Applies a gain curve to the given weight value that increases its distance to zero.

    :param value:   intensity value of the brush stroke
                     - float 0.0 - 1.0
    :param weight:  current weight value of the given vertex
                     - float 0.0 - 1.0

    :return result: modified weight value
                     - float 0.0 - 1.0
    """
    return min(weight + (weight * value), 1.0)  # add gain value and clamp between 0.0 and 1.0
# ----------------------------------------------------------------------------------------------- #