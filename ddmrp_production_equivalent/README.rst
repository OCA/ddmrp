.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
MRP BoM Equivalences when MO is created
=======================================

When a manufacturing order is created, Odoo uses the bill of material to determine 
which parts must be consumed without checking their availability. 

This module uses an equivalent part if the part on the BOM is not available..


Usage
=====
* Using DDMRP mechanism, If the main part on the BOM is not available (netflow position is in the red or yellow zone) 
  and equivalences can be used, use the first part (based on priority) that have a netflow position in the green zone.

* As an example, when a manufacturing order is created:
  if Part A from the BOM is available (quantity on hand > requested quantity):
     use Part A
  Otherwise
      If equivalences can be used:
          Get all the other parts in the same product category
          Exclude the non-equivalent parts listed in the BOM line
          Sort the remaining parts by their priority
          Use the first one
      Otherwise:
          Use Part A

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Antonio Yamuta <ayamuta@opensourceintegrators.com>
* Maxime Chambreuil <mchambreuil@opensourceintegrators.com>

Funders
-------

The development of this module has been financially supported by:

* Open Source Integrators <http://www.opensourceintegrators.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
