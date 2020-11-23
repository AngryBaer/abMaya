
# ----------------------------------------------------------------------------------------------- #
# IMPORTS
from math import pow, sqrt
from scipy.stats import norm
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
# True constrast operation that preserves minimum and maximum values.
def contrast(value, weightList, vtxMin, vtxMax):
    """ sharpen edge of active weight map """
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
