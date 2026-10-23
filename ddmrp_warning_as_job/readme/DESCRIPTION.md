This module makes the scheduled action *DDMRP Buffer Warning calculation*
(provided by **ddmrp_warning**) enqueue one queue job per stock buffer
instead of computing the warnings of all the buffers in a single
transaction. The jobs run in the `root.ddmrp` channel (provided by
**ddmrp_cron_actions_as_job**) and, thanks to identity keys, only one
pending job exists at a time for the same buffer.

Technically, the `<stock.buffer>._generate_ddmrp_warnings` method is
automatically delayed when the context contains
`auto_delay_ddmrp_generate_ddmrp_warnings=True`. The scheduled action
sets this key; the **Refresh Warnings** button of the buffer form does
not, so a manual refresh is still computed immediately.
