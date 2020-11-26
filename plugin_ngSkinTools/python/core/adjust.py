
# IMPORTS --------------------------------------------------------------------------------------- #
from math import pow, sqrt
from scipy.stats import norm
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
def contrast(value, weightList, vtxMin, vtxMax):
    """
    True contrast operation that preserves minimum and maximum values.
    Applies a curve to the given list of weight values that increases their distance to the
    average value.

    :param value:       intensity value of the operation
                        - float 0.0 - 1.0
    :param weightList:  current weight values of all vertices
                        - list [float, float, ...]
    :param vtxMin:      minimum weight values of all vertices
                        - float 0.0 - 1.0
    :param vtxMax:      maximum weight values of all vertices
                        - float 0.0 - 1.0

    :return result:     modified weight values
                        - list [float, float, ...]
    """
    avg = (vtxMax + vtxMin) / 2.0
    norm_range = vtxMax - vtxMin

    applied_list = []
    for weight in weightList:
        if not vtxMax > weight > vtxMin:
            applied_list.append(weight)
            continue
        difference = weight - avg
        multiplier = norm.cdf(difference, loc=0, scale=(0.1 * norm_range)) - weight
        result = max(vtxMin, min((weight + value * multiplier), vtxMax))
        applied_list.append(result)

    return applied_list
# ----------------------------------------------------------------------------------------------- #
