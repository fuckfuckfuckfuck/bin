# MUST BE COMBINED WITH fill strategy

from pyalgotrade.broker.slippage import SlippageModel
from numpy import sqrt

class MyVolumeShareSlippage(SlippageModel):
    """
    A volume share slippage model as defined in Zipline's VolumeShareSlippage model.
    The slippage is calculated by multiplying the price impact constant by the square of the ratio of the order
    to the total volume.

    Check https://www.quantopian.com/help#ide-slippage for more details.

    :param priceImpact: Defines how large of an impact your order will have on the backtester's price calculation.
    :type priceImpact: float.
    """

    def __init__(self, priceImpact=0.1):
        self.__priceImpact = priceImpact

    def calculatePrice(self, order, price, quantity, bar, volumeUsed):
        assert bar.getVolume(), "Can't use 0 volume bars with VolumeShareSlippage"

        totalVolume = volumeUsed + quantity
        volumeShare = totalVolume / float(bar.getVolume())
        # impactPct = volumeShare ** 2 * self.__priceImpact
        impactPct = sqrt(volumeShare) * self.__priceImpact
        if order.isBuy():
            ret = price * (1 + impactPct)
        else:
            ret = price * (1 - impactPct)
        return ret
