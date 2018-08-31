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
~~~~~~~

To list the list of inventory buffers, go to one of the following:
* *Inventory / Master Data / Stock Buffer Planning*
* *Inventory / Master Data / Reordering Rules*


Buffer Profiles
~~~~~~~~~~~~~~~
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

Usual factors should range from 0.2 (long lead time) to 0.8 (short lead time).


Product attributes
~~~~~~~~~~~~~~~~~~

* For manufactured products, go to *Manufacturing / Products* and
  update the 'Manufacturing Lead Time' field, available in the tab *Inventory*.
* For purchased products, go to go to *Purchasing / Products* and update the
  *Delivery Lead Time* for each vendor, available in tab *Purchase* and section
  *Vendors*.


ADU Calculation Methods
~~~~~~~~~~~~~~~~~~~~~~~

The Average Daily Usage (ADU) defines the frequency of demand of a product in a
certain location. It can be computed in different ways, which you can configure
with ADU calculation methods as follows:

#. Go to *Inventory / Configuration / DDMRP / ADU calculation methods*.
#. Indicate a name, a calculation method (fixed, past-looking,
   future-looking or blended).
#. Fill the corresponding period (past, future or both for blended method) to
   specify the length of period consideration (in days).
#. Indicate the source of information: stock moves or demand estimates.
#. If you use the blended method fill also the *Past Factor* and
   *Future Factor*.

If you do not have prior history of stock moves in your system, it is advised
to use fixed method or start to work on future estimates. If you have
past-history of stock moves, best use past-looking method or blended method.

The ADU is computed every day by default in a background job independently
from the other buffer fields. This computation can be done with less frequency
but it is not recommended to run it less than weekly or more than daily.
Circumstantially, If you need to force the calculation of the ADU go to
*Inventory / Configuration / DDMRP / Run DDMRP* and click on
*Run ADU calculation*.
