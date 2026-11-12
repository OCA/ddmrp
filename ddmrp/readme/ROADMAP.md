The DDMRP
[roadmap](https://github.com/OCA/ddmrp/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement)
and [known
issues](https://github.com/OCA/ddmrp/issues?q=is%3Aopen+is%3Aissue+label%3Abug)
can be found on GitHub.

The migration to 20.0 does not include migration scripts yet. They are
needed to upgrade databases from 19.0: the access rights and record rules
moved to `ir.access`, and the modules `stock_location_is_sublocation` and
`stock_move_quantity_product_uom` are no longer dependencies.
