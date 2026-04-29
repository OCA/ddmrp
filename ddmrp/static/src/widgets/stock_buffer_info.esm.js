import {Component, markup, onWillStart} from "@odoo/owl";
import {FloatField, floatField} from "@web/views/fields/float/float_field";
import {loadBokehLibraries} from "@web_widget_bokeh_chart/js/web_widget_bokeh_chart.esm";
import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";

export class StockBufferPopover extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        onWillStart(async () => {
            await loadBokehLibraries();
            var bufferId = this.props.record.resId;
            var bufferField = this.props.buffer_id;
            if (bufferField && this.props.record.data[bufferField]) {
                if (
                    ("field" in this.props.record.data[bufferField] &&
                        this.props.record.data[bufferField].field.type ===
                            "many2many") ||
                    bufferField.endsWith("_ids")
                ) {
                    if (this.props.record.data[bufferField].records.length > 0) {
                        bufferId = this.props.record.data[bufferField].records[0].resId;
                    } else {
                        // Relation is blank, no buffer.
                        bufferId = 0;
                    }
                } else {
                    // Assume m2o
                    bufferId = this.props.record.data[bufferField][0];
                }
            } else if (bufferField) {
                // Relation is blank, no buffer.
                bufferId = 0;
            }
            if (bufferId === 0) {
                return;
            }
            this.bokeh_chart = await this.orm.read(
                "stock.buffer",
                [bufferId],
                [this.props.field]
            );
        });
    }
    get json_value() {
        try {
            var value = JSON.parse(this.bokeh_chart[0][this.props.field]);
            value.div = markup(value.div.trim());
            return value;
        } catch {
            return {};
        }
    }
}
StockBufferPopover.template = "ddmrp.StockBufferPopover";

export class StockBufferInfoWidget extends FloatField {
    static components = {
        Popover: StockBufferPopover,
    };
    static props = {
        ...FloatField.props,
        color_from: {type: String, optional: true},
        field: {type: String, optional: true},
        buffer_id: {type: String, optional: true},
    };

    setup() {
        super.setup();
        this.popover = usePopover(StockBufferPopover, {position: "bottom-start"});
    }

    get classFromDecoration() {
        var decorationName = this.props.record.data[this.props.color_from];
        if (decorationName !== "" && decorationName.length > 1) {
            decorationName = "circle" + decorationName.slice(1);
            return `${decorationName}`;
        }
        return "";
    }

    showPopup(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this.popover.open(
            ev.currentTarget,
            {
                bus: this.bus,
                record: this.props.record,
                field: this.props.field,
                color_from: this.props.color_from,
                buffer_id: this.props.buffer_id,
            },
            {
                position: "right",
            }
        );
    }
}

StockBufferInfoWidget.template = "ddmrp.StockBufferInfoWidget";
export const stockBufferInfoWidget = {
    ...floatField,
    component: StockBufferInfoWidget,
};

const StockBufferInfoWidgetExtractProps = stockBufferInfoWidget.extractProps;

stockBufferInfoWidget.extractProps = ({attrs, options}) => {
    return Object.assign(StockBufferInfoWidgetExtractProps({attrs, options}), {
        color_from: options.color_from,
        field: options.field,
        buffer_id: options.buffer_id,
    });
};

registry.category("fields").add("stock_buffer_info", stockBufferInfoWidget);
