.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License AGPL-3

=================
DDMRP Adjustments
=================

Allow to extend DDMRP App to be able to apply Adjustments for dynamically
altering buffers for planned or anticipated events. This include:

* **Demand Adjustment Factor (DAF)**: is a manipulation of the ADU input
  within a specific time period. The system will look for existing DAFs when
  computing the ADU for each buffer and apply them. The system will also
  explode the resulting increase in demand of parent buffers to all their
  children buffers using the BoM.
* Zone Adjustment Factor (ZAF): pending to implement
* Lead Time Adjustment Factor pending to implement

Usage
-----

To plan buffer adjustments act as follows:

#. Click on *Inventory > Demand Planning > Create Buffer Adjustments*.
#. In the popup window fill the *Period* and *Date Range Type* to perform
   your planning.
#. Check the boxes of the *Factor to Apply* in which you are interested.
#. Select the DDMRP Buffers where to apply this factors.
#. Under the title *Sheet* you will see a generated sheet in which you can
   fill the values for each period.
#. Click *Validate* to confirm your planning and the system will end up
   showing you the newly created DDMRP adjustment records.

Bug Tracker
-----------

Bugs are tracked on `GitHub Issues
<https://github.com/Eficent/ddmrp/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Roadmap
-------

* simulation charts.
* implement new factors

Tasks to add new factors:

* Add factor to search view.
* Add factor in wizard
* Apply where appropriate.

Credits
-------

Contributors
============

* Lois Rilo <lois.rilo@eficent.com>
* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
==========

This module is maintained by the Eficent.
