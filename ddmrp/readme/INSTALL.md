We strongly recommend to modify the configuration of the reservation
method to manual in the outgoing operation types (so deliveries related
to Sales Orders aren't automatically reserved) and to avoid to reserve
stock for specific moves, buffers are in fact a reservation of stock.
However, while **reservation is discouraged**, it is still available to
be used, in case of reserved stock be aware that the buffer will be
blind to this transfers and stock and you are bypassing the DDMRP
reordering flow.
