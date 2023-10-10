/** @odoo-module **/

import {BomOverviewDisplayFilter} from "@mrp/components/bom_overview_display_filter/mrp_bom_overview_display_filter";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewDisplayFilter.prototype, "ddmrp", {
    setup() {
        this._super.apply();
        this.displayOptions.is_buffered = this.env._t("Buffered");
    },
});

patch(BomOverviewDisplayFilter, "ddmrp", {
    props: {
        ...BomOverviewDisplayFilter.props,
        showOptions: {
            ...BomOverviewDisplayFilter.showOptions,
            is_buffered: Boolean,
        },
    },
});
