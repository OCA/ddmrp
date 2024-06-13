/** @odoo-module **/
import {BomOverviewDisplayFilter} from "@mrp/components/bom_overview_display_filter/mrp_bom_overview_display_filter";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewDisplayFilter.prototype, {
    setup() {
        super.setup();
        this.displayOptions.is_buffered = _t("Buffered");
    },
});

patch(BomOverviewDisplayFilter, {
    props: {
        ...BomOverviewDisplayFilter.props,
        showOptions: {
            ...BomOverviewDisplayFilter.showOptions,
            is_buffered: Boolean,
        },
    },
});
