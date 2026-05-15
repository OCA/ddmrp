
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/ddmrp&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/ddmrp/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/ddmrp/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/ddmrp/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/ddmrp/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/ddmrp/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/ddmrp)
[![Translation Status](https://translation.odoo-community.org/widgets/ddmrp-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/ddmrp-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# ddmrp

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[ddmrp](ddmrp/) | 17.0.1.9.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Demand Driven Material Requirements Planning
[ddmrp_adjustment](ddmrp_adjustment/) | 17.0.1.2.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Allow to apply factor adjustments to buffers.
[ddmrp_chatter](ddmrp_chatter/) | 17.0.1.0.0 |  | Adds chatter and activities to stock buffers.
[ddmrp_cron_actions_as_job](ddmrp_cron_actions_as_job/) | 17.0.1.0.1 |  | Run DDMRP Buffer Calculation as jobs
[ddmrp_exclude_moves_adu_calc](ddmrp_exclude_moves_adu_calc/) | 17.0.1.1.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Define additional rules to exclude certain moves from ADU calculation
[ddmrp_exclude_moves_adu_calc_sales](ddmrp_exclude_moves_adu_calc_sales/) | 17.0.2.0.0 | <a href='https://github.com/DavidJForgeFlow'><img src='https://github.com/DavidJForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='DavidJForgeFlow'/></a> | DDMRP Exclude Moves ADU Calc integration with Sales app.
[ddmrp_history](ddmrp_history/) | 17.0.1.0.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Allow to store historical data of DDMRP buffers.
[ddmrp_include_location_final](ddmrp_include_location_final/) | 17.0.1.0.0 | <a href='https://github.com/DavidJForgeFlow'><img src='https://github.com/DavidJForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='DavidJForgeFlow'/></a> | This module implements the final location logic of v18 added in v17 by stock_push_delay to DDMRP logic.
[ddmrp_product_replace](ddmrp_product_replace/) | 17.0.1.2.0 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Provides a assisting tool for product replacement.
[ddmrp_report_part_flow_index](ddmrp_report_part_flow_index/) | 17.0.1.0.1 | <a href='https://github.com/JordiBForgeFlow'><img src='https://github.com/JordiBForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='JordiBForgeFlow'/></a> <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Provides the DDMRP Parts Flow Index Report
[ddmrp_warning](ddmrp_warning/) | 17.0.1.1.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Adds configuration warnings on stock buffers.
[ddmrp_warning_as_job](ddmrp_warning_as_job/) | 17.0.1.0.0 |  | Run DDMRP Warning as jobs

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
