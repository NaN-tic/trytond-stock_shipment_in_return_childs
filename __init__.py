# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .shipment import *


def register():
    Pool.register(
        ShipmentInReturn,
        module='stock_shipment_in_return_childs', type_='model')
