/* global moment */
odoo.define("mrp_workorder_timeline_week_load.TimelineRenderer", function (require) {
    "use strict";

    const core = require("web.core");
    const TimelineRenderer = require("web_timeline.TimelineRenderer");

    const _t = core._t;
    // Scale of the load according to the length of the visible window (in days)
    const SCALES = [
        {scale: "day", maxDays: 1.5},
        {scale: "week", maxDays: 8},
        {scale: "month", maxDays: 35},
    ];

    TimelineRenderer.include({
        /**
         * @override
         */
        init_timeline: function () {
            this._super.apply(this, arguments);
            this.timeline.on("rangechanged", () => this.refreshPeriodLoad(false));
        },

        /**
         * Add the load of the visible period to the groups of work centers.
         *
         * @override
         */
        split_groups: async function (events, group_bys) {
            const groups = await this._super.apply(this, arguments);
            if (!this._isPeriodLoadGrouping(group_bys)) {
                this._baseGroups = false;
                return groups;
            }
            this._baseGroups = groups;
            this._period = this._getVisiblePeriod();
            const load = await this._fetchPeriodLoad(this._period);
            return this._decorateGroups(groups, load);
        },

        /**
         * Refresh the load of the groups.
         *
         * @param {Boolean} force Recompute even if the period did not change
         */
        refreshPeriodLoad: async function (force) {
            if (!this._baseGroups) {
                return;
            }
            const period = this._getVisiblePeriod();
            if (!force && this._isSamePeriod(period, this._period)) {
                return;
            }
            this._period = period;
            const load = await this._fetchPeriodLoad(period);
            if (!this._isSamePeriod(period, this._period)) {
                return; // the window moved again meanwhile
            }
            this.timeline.setGroups(this._decorateGroups(this._baseGroups, load));
        },

        _isPeriodLoadGrouping: function (group_bys) {
            return (
                this.modelName === "mrp.workorder" &&
                group_bys.length > 0 &&
                _.first(group_bys) === "workcenter_id"
            );
        },

        _isSamePeriod: function (period_a, period_b) {
            if (!period_a || !period_b) {
                return !period_a && !period_b;
            }
            return period_a.date === period_b.date && period_a.scale === period_b.scale;
        },

        /**
         * Scale and reference date of the visible window. The scale comes from the
         * length of the window; the reference date is the day it starts on.
         * The server turns them into the natural day, week or month.
         *
         * @private
         * @returns {Object|Boolean} {scale, date}, or false if the window is too wide
         */
        _getVisiblePeriod: function () {
            const visible = this.timeline.getWindow();
            const start = moment(visible.start);
            const days = moment(visible.end).diff(start, "days", true);
            const definition = _.find(SCALES, (item) => days <= item.maxDays);
            if (!definition) {
                return false;
            }
            return {scale: definition.scale, date: start.format("YYYY-MM-DD")};
        },

        /**
         * @private
         * @returns {Promise<Object>} load indexed by work center id
         */
        _fetchPeriodLoad: function (period) {
            const ids = _.pluck(
                _.filter(this._baseGroups, (group) => group.id > 0),
                "id"
            );
            if (!period || !ids.length) {
                return Promise.resolve({});
            }
            return this._rpc({
                model: "mrp.workcenter",
                method: "get_period_load",
                args: [period.date, period.scale, ids],
                context: this.getSession().user_context,
            }).then((result) => _.indexBy(result, "workcenter_id"));
        },

        /**
         * @private
         * @returns {Array} copy of the groups with the load in their content
         */
        _decorateGroups: function (groups, load) {
            const scales = {day: _t("Day"), week: _t("Week"), month: _t("Month")};
            return _.map(groups, (group) => {
                const vals = load[group.id];
                if (!vals) {
                    return group;
                }
                const over = vals.available_hours < 0 ? " o_period_load_over" : "";
                const period =
                    vals.period_start === vals.period_end
                        ? vals.period_start
                        : `${vals.period_start} → ${vals.period_end}`;
                return _.extend({}, group, {
                    content:
                        `${group.content} <span class="o_period_load${over}" ` +
                        `title="${scales[vals.scale]}: ${period}">${vals.label}</span>`,
                });
            });
        },
    });
});
