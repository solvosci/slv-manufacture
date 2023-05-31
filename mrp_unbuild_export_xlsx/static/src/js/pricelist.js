odoo.define('product_pricelist_mgmt_advanced.custom_js', function(require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function($) {

        $('.pricelist_portal_button').on("click", function (event) {
            event.stopPropagation();
            event.stopImmediatePropagation();
            $("#charging").css("display", "inline-block");
        });

        $('#exportStandard').on("click", function (event) {
            $("#charging").css("display", "inline-block");
            var date_temp = $('[name="field_date"]')[0].value
            var field_date = {"date": date_temp}
            $.ajax({
                type: "GET",
                url: "/my/purchase/pricelist/export",
                data: field_date,
                xhrFields:{
                    responseType: 'blob'
                },
                success: function (result) {
                    console.log(result)
                    var blob = result;
                    var downloadUrl = URL.createObjectURL(blob);
                    var a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = "price_report.xlsx";
                    document.body.appendChild(a);
                    a.click();
                    $("#charging").css("display", "none");
                }
            });
        });

        $('#exportComparative').on("click", function (event) {
            $("#charging").css("display", "inline-block");
            var field_date_start = $('[name="field_date_start"]')[0].value
            var field_date_end = $('[name="field_date_end"]')[0].value
            var field_dates = {field_date_start: field_date_start, field_date_end: field_date_end}
            $('td[name="tcol1"]')
            $.ajax({
                type: "GET",
                url: "/my/purchase/pricelist/comparative/export",
                data: field_dates,
                xhrFields:{
                    responseType: 'blob'
                },
                success: function (result) {
                    console.log(result)
                    var blob = result;
                    var downloadUrl = URL.createObjectURL(blob);
                    var a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = "price_report.xlsx";
                    document.body.appendChild(a);
                    a.click();
                    $("#charging").css("display", "none");
                }
            });
        });

    });
});
