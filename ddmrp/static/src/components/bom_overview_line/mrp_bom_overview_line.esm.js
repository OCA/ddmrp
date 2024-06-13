/** @odoo-module **/

import {BomOverviewLine} from "@mrp/components/bom_overview_line/mrp_bom_overview_line";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewLine, {
    props: {
        ...BomOverviewLine.props,
        showOptions: {
            ...BomOverviewLine.showOptions,
            is_buffered: Boolean,
        },
    },
});
