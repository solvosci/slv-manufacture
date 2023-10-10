odoo.define('mrp_production_bom_preview_report.mrp_preview_bom_report', function (require) {
'use strict';

var core = require('web.core');
var stock_report_generic = require('stock.stock_report_generic');

var MrpPreviewBomReport = stock_report_generic.extend({
    events: {
        'click .o_mrp_bom_action': '_onClickAction'
    },
    get_html: function() {
        var self = this;
        var args = [
            this.given_context.active_id,
        ];
        return this._rpc({
                model: 'report.mrp_production_bom_preview_report.mrp_preview_bom_report',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
            });
    },
    set_html: function() {
        var self = this;
        return this._super().then(function () {
            self.$('.o_content').html(self.data.order);
        });
    },
    _onClickAction: function (ev) {
        ev.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            context: {
                'active_id': $(ev.currentTarget).data('res-id')
            },
            views: [[false, 'form']],
            target: 'current'
        });
    },
});

core.action_registry.add('mrp_preview_bom_report', MrpPreviewBomReport);
return MrpPreviewBomReport;

});
