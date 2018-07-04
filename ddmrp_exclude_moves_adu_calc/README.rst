.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
DDMRP Exclude Moves ADU Calc
============================

This module adds new criteria to exclude moves from the calculation of the
Average Dailiy Usage on an Orderpoint (Buffer), based on:

* Locations
* Specific stock moves

Usage
=====

You can exclude specific moves or all moves towards a specific location:

* Go to *Inventory > Reports > Stock Moves* and check the box *Exclude this
  move from ADU calculation* for a specific move.
* Go to *Inventory > Configuration > WH Management > Locations* and check the
  flag *Exclude this location from ADU calculation* for the desired locations.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Eficent/ddmrp/issues>`_. In case of
trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Lois Rilo Antelo <lois.rilo@eficent.com>

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
