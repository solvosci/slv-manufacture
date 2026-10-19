odoo.define("mrp_workorder_timeline_week_load.TimelineController", function (require) {
    "use strict";

    const TimelineController = require("web_timeline.TimelineController");

    TimelineController.include({
        /**
         * Created and removed records change the load of the work centers, but
         * the base controller does not reload the groups in these cases.
         */
        create_completed: function () {
            return this._super.apply(this, arguments).then(() => {
                this.renderer.refreshPeriodLoad(true);
            });
        },

        remove_completed: function () {
            return this._super.apply(this, arguments).then(() => {
                this.renderer.refreshPeriodLoad(true);
            });
        },
    });
});
