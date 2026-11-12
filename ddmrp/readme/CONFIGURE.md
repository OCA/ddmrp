## Scheduled actions

- Go to *Settings \> Technical*.
- 'DDMRP Buffer ADU calculation'. Computes the Average Daily Usage for
  all Buffers.
- 'Reordering Rule DDMRP calculation'. Computes the Qualified Demand,
  Net Flow Position, Planning and Execution priorities for all Buffers.

## Decoupled Lead Time computation

The DLT is automatically computed by the system.

For manufactured products' buffers just remember to provide and set
properly the following information:

- The *Manufacturing Lead Time* for the manufactured product. It can be
  found at the product form view under the tab *Sales*.
- The *Delivery Lead Time* for the preferred vendor of a product. This
  is important for the products which are purchased and are components
  in any Bill of Materials.

For purchased/distributed products' buffers the logic is simpler.

- In the first place the system will look if there are Vendors for the
  product, if so it will use the *Delivery Lead Time* of the preferred
  one.
- In case of absence of vendors, the *Lead Time* at the bottom of the
  Buffer form view will be used.
