/** @odoo-module **/

import {FloatField} from "@web/views/fields/float/float_field";
import {loadBundle} from "@web/core/assets";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {useUniquePopover} from "@web/core/model_field_selector/unique_popover_hook";

const {Component, markup, onWillStart} = owl;

export class StockBufferPopover extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        onWillStart(async () => {
            await loadBundle({
                jsLibs: [
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-api-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-widgets-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-tables-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-mathjax-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-gl-3.1.1.min.js",
                ],
            });
            this.bokeh_chart = await this.orm.read(
                this.props.record.resModel,
                [this.props.record.resId],
                [this.props.field]
            );
        });
    }
    get json_value() {
        try {
            var value = JSON.parse(this.bokeh_chart[0][this.props.field]);
            value.div = markup(value.div.trim());
            return value;
        } catch (error) {
            return {};
        }
    }
}
StockBufferPopover.template = "ddmrp.StockBufferPopover";

export class StockBufferInfoWidget extends FloatField {
    setup() {
        super.setup();
        this.popover = useUniquePopover();
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
        this.popover.add(
            ev.currentTarget,
            this.constructor.components.Popover,
            {
                bus: this.bus,
                record: this.props.record,
                field: this.props.field,
                color_from: this.props.color_from,
            },
            {
                position: "right",
            }
        );
    }
}

StockBufferInfoWidget.components = {
    ...StockBufferInfoWidget.components,
    Popover: StockBufferPopover,
};
StockBufferInfoWidget.template = "ddmrp.StockBufferInfoWidget";

StockBufferInfoWidget.props = {
    ...StockBufferInfoWidget.props,
    color_from: {type: String, optional: true},
    field: {type: String, optional: true},
};

const StockBufferInfoWidgetExtractProps = StockBufferInfoWidget.extractProps;
StockBufferInfoWidget.extractProps = ({attrs, field}) => {
    return Object.assign(StockBufferInfoWidgetExtractProps({attrs, field}), {
        color_from: attrs.options.color_from,
        field: attrs.options.field,
    });
};

registry.category("fields").add("stock_buffer_info", StockBufferInfoWidget);
