import {BomOverviewTable} from "@mrp/components/bom_overview_table/mrp_bom_overview_table";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewTable.prototype, {
    // ---- Getters ----

    get showBuffered() {
        return this.props.showOptions.is_buffered;
    },
});
