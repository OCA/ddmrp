
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# DDMRP
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/ddmrp&target_branch=15.0)
[![Pre-commit Status](https://github.com/OCA/ddmrp/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/OCA/ddmrp/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/OCA/ddmrp/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/OCA/ddmrp/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/OCA/ddmrp/branch/15.0/graph/badge.svg)](https://codecov.io/gh/OCA/ddmrp)
[![Translation Status](https://translation.odoo-community.org/widgets/ddmrp-15-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/ddmrp-15-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

Demand Driven Material Requirements Planning implementation for Odoo.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[ddmrp](ddmrp/) | 15.0.1.17.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> <a href='https://github.com/ChrisOForgeFlow'><img src='https://github.com/ChrisOForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='ChrisOForgeFlow'/></a> | Demand Driven Material Requirements Planning
[ddmrp_adjustment](ddmrp_adjustment/) | 15.0.1.5.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Allow to apply factor adjustments to buffers.
[ddmrp_chatter](ddmrp_chatter/) | 15.0.1.0.1 |  | Adds chatter and activities to stock buffers.
[ddmrp_coverage_days](ddmrp_coverage_days/) | 15.0.1.2.0 |  | Implements Coverage Days.
[ddmrp_cron_actions_as_job](ddmrp_cron_actions_as_job/) | 15.0.1.0.0 |  | Run DDMRP Buffer Calculation as jobs
[ddmrp_exclude_moves_adu_calc](ddmrp_exclude_moves_adu_calc/) | 15.0.1.0.1 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Define additional rules to exclude certain moves from ADU calculation
[ddmrp_history](ddmrp_history/) | 15.0.1.3.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Allow to store historical data of DDMRP buffers.
[ddmrp_packaging](ddmrp_packaging/) | 15.0.1.0.0 |  | DDMRP integration with packaging
[ddmrp_product_replace](ddmrp_product_replace/) | 15.0.1.2.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Provides a assisting tool for product replacement.
[ddmrp_report_part_flow_index](ddmrp_report_part_flow_index/) | 15.0.1.3.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Provides the DDMRP Parts Flow Index Report
[ddmrp_warning](ddmrp_warning/) | 15.0.1.5.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds configuration warnings on stock buffers.
[stock_buffer_capacity_limit](stock_buffer_capacity_limit/) | 15.0.1.1.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Ensures that the limits of storage are never surpassed
[stock_buffer_route](stock_buffer_route/) | 15.0.1.2.0 |  | Allows to force a route to be used when procuring from Stock Buffers
[stock_buffer_sales_analysis](stock_buffer_sales_analysis/) | 15.0.1.0.0 |  | Allows to access the Sales Analysis from Stock Buffers

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
