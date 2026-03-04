Glue module between **DDMRP** and **Purchase Order Approved**.

The `purchase_order_approved` module adds an intermediate "approved" state to
purchase orders. Without this glue module, DDMRP ignores PO lines in the
"approved" state because `_get_rfq_dlt()` only considers draft, sent, and
to-approve states.

This module extends the `_get_unconfirmed_po_states()` hook on `stock.buffer`
to include the "approved" state, ensuring that approved purchase orders are
visible to DDMRP buffer calculations.
