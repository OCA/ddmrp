/** @odoo-module **/

import {FloatField} from "@web/views/fields/float/float_field";
import {formatDateTime} from "@web/core/l10n/dates";
import {loadBundle} from "@web/core/assets";
import {localization} from "@web/core/l10n/localization";
import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";

const {Component, EventBus, onWillRender, onWillStart, markup} = owl;

export class StockBufferPopover extends Component {
    setup() {
        this.actionService = useService("action");
        onWillStart(() =>
            loadBundle({
                jsLibs: [
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-api-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-widgets-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-tables-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-mathjax-3.1.1.min.js",
                    "/web_widget_bokeh_chart/static/src/lib/bokeh/bokeh-gl-3.1.1.min.js",
                ],
            })
        );
    }
    get json_value() {
        try {
            var value = JSON.parse(this.props.record.data[this.props.field]);
            value.div = markup(value.div.trim());
            return value;
        } catch (error) {
            return {};
        }
    }

    openForecast() {
        this.actionService.doAction(
            "stock.stock_replenishment_product_product_action",
            {
                additionalContext: {
                    active_model: "product.product",
                    active_id: this.props.record.data.product_id[0],
                    warehouse:
                        this.props.record.data.warehouse_id &&
                        this.props.record.data.warehouse_id[0],
                    move_to_match_ids: this.props.record.data.move_ids.records.map(
                        (record) => record.data.id
                    ),
                    sale_line_to_match_id: this.props.record.data.id,
                },
            }
        );
    }
}
StockBufferPopover.template = "ddmrp.StockBufferPopover";

export class StockBufferInfoWidget extends FloatField {
    setup() {
        super.setup();
        this.bus = new EventBus();
        this.popover = usePopover();
        this.closePopover = null;
        this.calcData = {};
        onWillRender(() => {
            this.initCalcData();
        });
    }

    get classFromDecoration() {
        var decorationName = this.props.record.data[this.props.color_from];
        if (decorationName !== "" && decorationName.length > 1) {
            decorationName = "circle" + decorationName.slice(1);
            return `${decorationName}`;
        }
        return "";
    }

    initCalcData() {
        // Calculate data not in record
        const {data} = this.props.record;
        if (data.scheduled_date) {
            // TODO: might need some round_decimals to avoid errors
            if (data.state === "sale") {
                this.calcData.will_be_fulfilled =
                    data.free_qty_today >= data.qty_to_deliver;
            } else {
                this.calcData.will_be_fulfilled =
                    data.virtual_available_at_date >= data.qty_to_deliver;
            }
            this.calcData.will_be_late =
                data.forecast_expected_date &&
                data.forecast_expected_date > data.scheduled_date;
            if (["draft", "sent"].includes(data.state)) {
                // Moves aren't created yet, then the forecasted is only based on virtual_available of quant
                this.calcData.forecasted_issue =
                    !this.calcData.will_be_fulfilled && !data.is_mto;
            } else {
                // Moves are created, using the forecasted data of related moves
                this.calcData.forecasted_issue =
                    !this.calcData.will_be_fulfilled || this.calcData.will_be_late;
            }
        }
    }

    updateCalcData() {
        // Popup specific data
        const {data} = this.props.record;
        if (!data.scheduled_date) {
            return;
        }
        this.calcData.delivery_date = formatDateTime(data.scheduled_date, {
            format: localization.dateFormat,
        });
        if (data.forecast_expected_date) {
            this.calcData.forecast_expected_date_str = formatDateTime(
                data.forecast_expected_date,
                {format: localization.dateFormat}
            );
        }
    }

    showPopup(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this.updateCalcData();
        if (!this.closePopover) {
            this.closePopover = this.popover.add(
                ev.currentTarget,
                this.constructor.components.Popover,
                {
                    bus: this.bus,
                    record: this.props.record,
                    calcData: this.calcData,
                    field: this.props.field,
                    color_from: this.props.color_from,
                },
                {
                    position: "right",
                }
            );
            this.bus.addEventListener("close-popover", this.closePopover);
        }
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
