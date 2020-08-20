odoo.define("ddmrp.list_renderer_buffer_info", function(require) {
    "use strict";

    var ListRenderer = require("web.ListRenderer");
    var concurrency = require("web.concurrency");

    ListRenderer.include({
        /**
         * Extend module to allow coloring taking into account the option attribute color_from
         *
         * @override
         */
        init: function(parent, state) {
            this.detailDP = new concurrency.DropPrevious();
            this.openedPopovers = [];
            this.field_buffer_type = "One2many";
            this.field_buffer_id = "id";
            if (state.model === "stock.buffer") {
                $(document.body).addClass("with-scrollbar");
            }
            this._super.apply(this, arguments);
        },
        _renderBodyCell: function(record, node, colIndex, options) {
            var $td = this._super.apply(this, arguments);
            options = node.attrs.options;
            if (typeof options === "string") {
                try {
                    options = JSON.parse(options);
                } catch (e) {
                    console.log("Error while parsing JSON " + e);
                }
            }
            if (options) {
                if (options.color_from) {
                    var color_field = options.color_from;
                    this._updateNodeStyle($td, record, node, color_field);

                    // Attach on click and body click listeners to show and hide popup
                    $td.children().on(
                        "click",
                        {record: record},
                        this._onCellClickListener.bind(this)
                    );
                    $(document).on("click", "*", this._onBodyClickListener.bind(this));
                }
                if (options.buffer_id) {
                    this.field_buffer_type = "One2many";
                    this.field_buffer_id = options.buffer_id;
                }
                if (options.buffer_ids) {
                    this.field_buffer_type = "Many2many";
                    this.field_buffer_id = options.buffer_ids;
                }
            }
            return $td;
        },
        _updateNodeStyle: function($td, record, node, color_field) {
            var text = $td.text();
            $td.text("");
            $td.css("text-align", "center");
            var span = $('<span class="circle">' + text + " %</span>");
            if (record.data[color_field]) {
                var color = record.data[color_field];
                if (color === "1_red") {
                    span.addClass("circle_red");
                } else if (color === "2_yellow") {
                    span.addClass("circle_yellow");
                } else if (color === "3_green") {
                    span.addClass("circle_green");
                } else if (color === "0_dark_red") {
                    span.addClass("circle_dark_red");
                }
                $td.append(span);
            }
        },
        _dismissAllPopovers: function() {
            // Remove popovers for all elements with class circle
            for (var i = 0; i < this.openedPopovers.length; i++) {
                var popover = $("#" + this.openedPopovers[i].attr("aria-describedby"));
                if (popover.data("bs.popover")) {
                    popover.popover("hide");
                    $("#currentPopoverScript").remove();
                    this.openedPopovers.pop(i);
                }
            }
        },

        // HANDLERS

        _onBodyClickListener: function() {
            if (this.openedPopovers.length !== 0) {
                this._dismissAllPopovers();
            }
        },

        _onCellClickListener: function(event) {
            // Stop from going to the form view
            event.preventDefault();
            event.stopPropagation();

            var self = this;
            var record = event.data.record;
            var target = event.currentTarget;

            var id = record.data[this.field_buffer_id];
            if (this.field_buffer_id !== "id") {
                if (this.field_buffer_type === "Many2many") {
                    id = id.res_ids[0];
                } else {
                    id = id.res_id;
                }
            }

            self._dismissAllPopovers();

            var genericCloseBtnHtml =
                '<button onclick="$(this).closest(\'div.popover\').popover(\'hide\');" type="button" class="close">&times;</button>';

            // Data request
            this.detailDP.add(
                this._rpc({
                    model: "stock.buffer",
                    method: "get_ddmrp_chart",
                    args: [id],
                }).then(function(result) {
                    var content = result[0];
                    var script = result[1];
                    var scriptCode = script.substring(
                        script.lastIndexOf('t">') + 4,
                        script.lastIndexOf("</script>")
                    );
                    var options = {
                        placement: "right",
                        trigger: "manual",
                        html: true,
                        title: "Buffer Status" + genericCloseBtnHtml,
                        content: content,
                    };
                    $(target).popover(options);
                    $(target)
                        .attr("data-content", content)
                        .data("bs.popover")
                        .setContent();
                    $(target).popover("show");
                    self.openedPopovers.push($(target));

                    var scriptNode = document.createElement("script");
                    scriptNode.type = "text/javascript";
                    scriptNode.id = "currentPopoverScript";
                    var code = scriptCode;
                    try {
                        scriptNode.appendChild(document.createTextNode(code));
                        document.body.appendChild(scriptNode);
                    } catch (e) {
                        scriptNode.text = code;
                        document.body.appendChild(scriptNode);
                    }
                })
            );
        },
        _onMouseLeaveListener: function() {
            this._dismissAllPopovers();
        },
    });
});
