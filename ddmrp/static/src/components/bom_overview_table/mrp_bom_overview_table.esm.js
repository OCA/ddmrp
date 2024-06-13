/** @odoo-module **/

import {BomOverviewTable} from "@mrp/components/bom_overview_table/mrp_bom_overview_table";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewTable.prototype, {
    // ---- Getters ----

    get showBuffered() {
        return this.props.showOptions.is_buffered;
    },
});

patch(BomOverviewTable, {
    props: {
        ...BomOverviewTable.props,
        showOptions: {
            ...BomOverviewTable.showOptions,
            is_buffered: Boolean,
        },
    },
});
