/** @odoo-module **/

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewComponent.prototype, "ddmrp", {
    setup() {
        this._super.apply();
        this.state.showOptions.is_buffered = true;
        this.state.showOptions.dlt = true;
    },

    async getWarehouses() {
        await this._super.apply();
        if (this.props.action.context.warehouse_id) {
            this.state.currentWarehouse = this.warehouses.filter(
                (warehouse) => warehouse.id === this.props.action.context.warehouse_id
            )[0];
        }
    },

    getReportName() {
        return (
            this._super.apply(this, arguments) +
            "&show_buffered=" +
            this.state.showOptions.is_buffered
        );
    },
});
