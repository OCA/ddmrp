/** @odoo-module **/

import {BomOverviewSpecialLine} from "@mrp/components/bom_overview_special_line/mrp_bom_overview_special_line";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewSpecialLine, {
    props: {
        ...BomOverviewSpecialLine.props,
        showOptions: {
            ...BomOverviewSpecialLine.showOptions,
            is_buffered: Boolean,
        },
    },
});
