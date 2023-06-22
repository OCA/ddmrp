
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/ddmrp&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/ddmrp/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/ddmrp/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/ddmrp/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/ddmrp/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/ddmrp/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/ddmrp)
[![Translation Status](https://translation.odoo-community.org/widgets/ddmrp-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/ddmrp-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# DDMRP

Demand Driven Material Requirements Planning implementation for Odoo.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[ddmrp](ddmrp/) | 13.0.1.29.5 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Demand Driven Material Requirements Planning
[ddmrp_adjustment](ddmrp_adjustment/) | 13.0.1.1.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allow to apply factor adjustments to buffers.
[ddmrp_chatter](ddmrp_chatter/) | 13.0.1.0.0 |  | Adds chatter and activities to stock buffers.
[ddmrp_coverage_days](ddmrp_coverage_days/) | 13.0.1.2.0 |  | Implements Coverage Days.
[ddmrp_cron_actions_as_job](ddmrp_cron_actions_as_job/) | 13.0.1.2.0 |  | Run DDMRP Buffer Calculation as jobs
[ddmrp_exclude_moves_adu_calc](ddmrp_exclude_moves_adu_calc/) | 13.0.1.0.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Define additional rules to exclude certain moves from ADU calculation
[ddmrp_history](ddmrp_history/) | 13.0.1.3.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allow to store historical data of DDMRP buffers.
[ddmrp_packaging](ddmrp_packaging/) | 13.0.1.7.0 |  | DDMRP integration with packaging
[ddmrp_product_replace](ddmrp_product_replace/) | 13.0.2.2.1 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Provides a assisting tool for product replacement.
[ddmrp_sale](ddmrp_sale/) | 13.0.1.2.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | DDMRP integration with Sales app.
[ddmrp_warning](ddmrp_warning/) | 13.0.1.2.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds configuration warnings on stock buffers.
[stock_buffer_capacity_limit](stock_buffer_capacity_limit/) | 13.0.1.1.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Ensures that the limits of storage are never surpassed
[stock_buffer_route](stock_buffer_route/) | 13.0.1.3.0 |  | Allows to force a route to be used when procuring from Stock Buffers
[stock_buffer_sales_analysis](stock_buffer_sales_analysis/) | 13.0.1.0.0 |  | Allows to access the Sales Analysis from Stock Buffers

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
