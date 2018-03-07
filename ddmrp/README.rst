.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

=====
DDMRP
=====

Demand Driven Material Requirements Planning is a formal multi-echelon
planning and execution method developed by Ms. Carol Ptak and Mr. Chad Smith.

DDMRP combines blended aspects of Material Requirements Planning (MRP),
Distribution Requirements Planning (DRP) with the pull and visibility
emphases found in Lean and the Theory of Constraints and the variability
reduction emphasis of Six Sigma.

This method has five sequential components:

#. *Strategic Inventory Positioning*. Answers the question "Given our system
   and environment, where should we place inventory to have the best
   protection?" and determines where should decoupling points of inventory be
   placed.

#. *Buffer Profiles and Levels*. Determine the amount of protection at those
   decoupling points.

#. *Dynamic Adjustments*. Allow the company to adapt buffers to group and
   individual part trait changes over time through the use of several types
   of adjustments.

#. *Demand Driven Planning*. Allow to launch purchase orders (POs),
   manufacturing orders (MOs) and Transfer Orders (TOs) based on the priority
   dictated by the buffers.

#. *Visible and Collaborative Execution*. These POs, MOs and TOs have to be
   effectively managed to synchronize with the changes that often occur within
   the "execution horizon."

These five components work together to greatly dampen, if not eliminate,
the nervousness of traditional MRP systems and the bullwhip effect in
complex and challenging environments.

This approach provides real information about those parts that are
truly at risk of negatively impacting the planned availability of inventory.

DDMRP sorts the significant few items that require attention from
the many parts that are being managed. Under the DDMRP approach,
fewer planners can make better decisions more quickly. That means companies
will be better able to leverage their working and human capital.

Demand Driven Material Requirements Planning is quickly being adopted
by a wide variety of leading companies across the world.

Some of the benefits reported by the DDMRP method include:

* High fill rate performance
* Lead time reductions
* Inventory reductions, while improving customer service
* Eliminate costs related to expedite
* Planners see priorities instead of constantly fighting the conflicting
  messages of MRP

It is highly recommended to read the book 'Demand Driven Material
Requirements Planning (DDMRP)' by Carol Ptak and Chad Smith.

Installation
============

To install this module you need to first download modules from other OCA
repositories:

Modules from http://github.com/OCA/web :

* 'web_tree_dynamic_colored_field'
* 'web_widget_bokeh_chart'
* 'web_tree_many2one_clickable'

Modules from http://github.com/OCA/stock-logistics-warehouse :

* 'stock_warehouse_orderpoint_stock_info'
* 'stock_warehouse_orderpoint_stock_info_unreserved'
* 'stock_available_unreserved'
* 'stock_orderpoint_uom'
* 'stock_orderpoint_manual_procurement'
* 'stock_demand_estimate'

Modules from http://github.com/OCA/server-tools

* 'base_cron_exclusion'

We strongly recommend to **uninstall** ``procurement_jit`` (so deliveries
related to Sales Orders aren't automatically reserved) and to avoid to
reserve stock for specific moves, buffers are in fact a reservation of stock.
However, while **reservation is discouraged**, it is still available to be
used, in case of reserved stock be aware that the buffer will be blind to this
transfers and stock and you are bypassing the DDMRP reordering flow.

Configuration
=============

Scheduled actions
-----------------

* Go to *Settings > Technical*.
* 'DDMRP Buffer ADU calculation'. Computes the Average Daily Usage for all
  Buffers.
* 'Reordering Rule DDMRP calculation'. Computes the Qualified Demand, Net
   Flow Position, Planning and Execution priorities for all Buffers.

Decoupled Lead Time computation
-------------------------------

The DLT is automatically computed by the system.

A) For manufactured products' buffers just remember to provide and
   set properly the following information:

* The *Manufacturing Lead Time* for the manufactured product. It can be found
  at the product form view under the tab *Sales*.
* The *Delivery Lead Time* for the preferred vendor of a product. This is
  important for the products which are purchased and are components in any
  Bill of Materials.

B) For purchased/distributed products' buffers the logic is simpler.

* In the first place the system will look if there are Vendors for the product,
  if so it will use the *Delivery Lead Time* of the preferred one.
* In case of absence of vendors, the *Lead Time* at the bottom of the Buffer
  form view will be used.

Usage
=====

To easily identify were are you maintaining buffers in your Bill of
Materials, you will need to first provide location information on the Bills
of Materials.

* Go to *Manufacturing / Products / Bill of Materials* and update the
  'Location' in all the Bill of Materials and associated lines,
  indicating where will the parts be placed/used during the manufacturing
  process.

* Print the report 'BOM Structure' to display where in your BOM are you
  maintaining buffers, and to identify the Lead Time (LT) of each product, and
  Decouple Lead Time (DLT).


Buffers
-------

To list the list of inventory buffers, go to one of the following:
* *Inventory / Inventory Control / Stock Buffer Planning*
* *Inventory / Inventory Control / Reordering Rules*


Buffer Profiles
---------------
Buffer profiles make maintenance of buffers easier by grouping them in
profiles. Changes applied to the profiles will be applicable in the
associated buffer calculations.

* Go to *Inventory / Configuration / Buffer Profiles*.

The Buffer Profile Lead Time Factor influences the size of the Buffer Green
zone. Items with longer lead times will usually have smaller green zones, which
will translate in more frequent supply order generation.

* Go to *Inventory / Configuration / Buffer Profile Lead Time Factor* to
  chan

The Buffer Profile Variability Factor influences the size of the Buffer Red
Safety zone. Items with longer lead times will usually have smaller green
zones, which will translate in more frequent supply order generation.

* Go to *Inventory / Configuration / Buffer Profile Lead Time Factor*.

Usual factors should range from 0.2 (long lead time) to 0.7 (short lead time).


Product attributes
------------------

* For manufactured products, go to *Manufacturing / Products* and
  update the 'Manufacturing Lead Time' field, available in the tab *Sales*.
* For purchased products, go to go to *Purchasing / Products* and update the
  *Delivery Lead Time* for each vendor, available in tab *Invenory* section
  *Vendors*.


ADU Calculation Methods
-----------------------

The Average Daily Usage (ADU) defines the frequency of demand of a product in a
certain location.

#. Go to *Inventory / Configuration / ADU calculation methods*.
#. To create new, indicate a name, calculation method (fixed, past-looking,
   future-looking), and the length of period consideration (in days).

If you do not have prior history of stock moves in your system, it is advised
to use fixed method. If you have past-history of stock moves, best use
past-looking method.



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_group_invoice_line%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Lois Rilo Antelo <lois.rilo@eficent.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
