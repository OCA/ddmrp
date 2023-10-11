/** @odoo-module **/

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewComponent.prototype, "ddmrp", {
    setup() {
        this._super.apply();
        this.state.showOptions.is_buffered = true;
        this.state.showOptions.dlt = true;
    },

    getReportName() {
        return (
            this._super.apply(this, arguments) +
            "&show_buffered=" +
            this.state.showOptions.is_buffered
        );
    },
});
