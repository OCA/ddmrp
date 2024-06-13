/** @odoo-module **/

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewComponent.prototype, {
    setup() {
        super.setup();
        this.state.showOptions.is_buffered = true;
        this.state.showOptions.dlt = true;
    },

    async getWarehouses() {
        await super.getWarehouses();
        if (this.props.action.context.warehouse_id) {
            this.state.currentWarehouse = this.warehouses.filter(
                (warehouse) => warehouse.id === this.props.action.context.warehouse_id
            )[0];
        }
    },

    getReportName(printAll) {
        return (
            super.getReportName(printAll) +
            "&show_buffered=" +
            this.state.showOptions.is_buffered
        );
    },
});
