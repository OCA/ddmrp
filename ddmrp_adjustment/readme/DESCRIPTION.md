Allow to extend DDMRP App to be able to apply Adjustments for
dynamically altering buffers for planned or anticipated events. This
include:

- **Demand Adjustment Factor (DAF)**: is a manipulation of the ADU input
  within a specific time period. The system will look for existing DAFs
  when computing the ADU for each buffer and apply them. The system will
  also explode the resulting increase in demand of parent buffers to all
  their children buffers using the BoM.
- **Lead Time Adjustment Factor (LTAF)**: manipulates the Decoupled Lead
  Time for an individual part or group of parts (buffer profile, same
  partner...) to adjust for a planned or known expansions of LT.
- Zone Adjustment Factor (ZAF): pending to implement
