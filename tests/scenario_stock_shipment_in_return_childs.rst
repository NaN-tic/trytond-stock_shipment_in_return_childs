========================================
Stock Shipment In Return Childs Scenario
========================================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from trytond.tests.tools import activate_modules
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)

Install product_cost_plan Module::

    >>> config = activate_modules('stock_shipment_in_return_childs')


Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])
    >>> child_loc = Location(name='child', parent=storage_loc)
    >>> child_loc.save()

Create a shipment in return for storage location::

    >>> ShipmentInReturn = Model.get('stock.shipment.in.return')
    >>> shipment = ShipmentInReturn()
    >>> shipment.supplier = supplier
    >>> shipment.from_location = storage_loc
    >>> shipment.to_location = supplier_loc
    >>> move = shipment.moves.new()
    >>> move.product = product
    >>> move.quantity = 1
    >>> move.from_location = storage_loc
    >>> move.to_location = supplier_loc
    >>> shipment.click('wait')
    >>> shipment.click('assign_try')
    False
    >>> shipment.state
    u'waiting'

Make 1 unit of the product available on child location::

    >>> StockMove = Model.get('stock.move')
    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 1
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = child_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.company = company
    >>> incoming_move.unit_price = Decimal('1')
    >>> incoming_move.click('do')

Now it picks the unit available from child location::

    >>> shipment.click('assign_try')
    True
    >>> shipment.state
    u'assigned'
    >>> move, = shipment.moves
    >>> move.from_location == child_loc
    True
