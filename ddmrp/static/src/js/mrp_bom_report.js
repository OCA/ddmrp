odoo.define("ddmrp.mrp_bom_report", function(require) {
    "use strict";

    var core = require("web.core");
    var MrpBomReport = require("mrp.mrp_bom_report");

    var DdmrpBomReport = MrpBomReport.extend({
        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.given_context.location_id = action.context.location_id || false;
        },
        get_bom: function(event) {
            var self = this;
            var $parent = $(event.currentTarget).closest("tr");
            var activeID = $parent.data("id");
            var productID = $parent.data("product_id");
            var lineID = $parent.data("line");
            var qty = $parent.data("qty");
            var level = $parent.data("level") || 0;
            return this._rpc({
                model: "report.mrp.report_bom_structure",
                method: "get_bom",
                args: [activeID, productID, parseFloat(qty), lineID, level + 1],
                context: this.given_context,
            }).then(function(result) {
                self.render_html(event, $parent, result);
            });
        },
    });

    core.action_registry.add("mrp_bom_report", DdmrpBomReport);
    return DdmrpBomReport;
});
