
# IMPORTS --------------------------------------------------------------------------------------- #
from math import pow, sqrt

from abMaya.libModel import component
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
    average = (vtxMax + vtxMin) / 2.0
    difference = weight - average

    if difference > 0:
        return min(weight + ((vtxMax - weight) * value), vtxMax)

    if difference == 0:
        return weight

    if difference < 0:
        return max(weight - ((weight - vtxMin) * value), vtxMin)



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