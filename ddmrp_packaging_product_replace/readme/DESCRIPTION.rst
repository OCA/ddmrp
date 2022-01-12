This is a glue module between `ddmrp_packaging` and `ddmrp_product_replace`.
It disable the copy of the packaging information when using the product
replacement wizard.
Without it the new stock buffer created have the packaging of the old product
set on them and the constraint `_check_product_packaging` raises an error.

Strangely, this is not happening with Odoo 13 ?
