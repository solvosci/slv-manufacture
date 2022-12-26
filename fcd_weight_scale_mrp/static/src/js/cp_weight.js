odoo.define('fcd_weight_scale_mrp.custom_js', function(require) {
    'use strict';

    var core = require('web.core');
    var _t = core._t;

    $('#fcd_weight_scale_mrp_portal').ready(function() {
        if ($("#chkpName").text() != "") {

            function asyncFunc(log) {
                return new Promise((resolve, reject) => {
                    // printJS(('/report/pdf/fcd_weight_scale_mrp.report_tag_pdf/' + log) => {
                    //     resolve("foo");
                    // },);
                    //
                    // function done_resolve(){
                    //     resolve("test")
                    // }
                    // printJS('/report/pdf/fcd_weight_scale_mrp.report_tag_pdf/' + log, {
                    //     onLoadingEnd: done_resolve
                    // });



                    printJS('/report/pdf/fcd_weight_scale_mrp.report_tag_pdf/' + log)
                    setTimeout(() =>
                        resolve("test"),
                    8000);
                });
            }
            const globalOptions = {
                position: "top-right",
                maxNotifications: 5,
                durations: {
                global: 3000
                }
            };
            globalOptions.labels = {
                async: _t("Printing"),
                info: _t("Printed"),
            };
            const notifier = new AWN(globalOptions);
            var myModal = new bootstrap.Modal(document.getElementById('areUSure'))

            //Inicializations

            let old_lot
            let old_product
            let old_family
            let endLot = false;
            let barcode_text = ""

            //Utility Functions

            function validation() {
                var flag = true;
                if ($("#productSelect" ).val() == $("#txt_translate_select_product").text()) {
                    flag = false;
                    notifier.alert($("#txt_translate_alert_no_product").text());
                }
                if ($("#typeBoxSelect" ).val() == $("#txt_translate_select_type_box").text()) {
                    flag = false;
                    notifier.alert($("#txt_translate_alert_no_type_box").text());
                }
                if ($("#lotSelect").val() == $("#txt_translate_select_lot").text()) {
                    flag = false;
                    notifier.alert($("#txt_translate_alert_no_lot").text());
                }
                if ($("#chkboxFixed").is(':checked') && (parseFloat($("#fixedQuantity").val()) <= 0 || isNaN(parseFloat($("#fixedQuantity").val())))) {
                    flag = false;
                    notifier.alert($("#txt_translate_alert_valid_value_fixed_weight_box").text());
                }
                if ($("#taring").attr('state') == 'active') {
                    if (parseFloat($("#weight").val()) <= 0) {
                        flag = false;
                        notifier.alert($("#txt_translate_alert_tare_greater_weight").text());
                    }
                }
                if ($("#weight").val() == "" || parseFloat($("#weight").val()) <= 0) {
                    flag = false;
                    notifier.alert($("#txt_translate_alert_connect_scale").text());
                }
                return flag;
            }

            function tareStyleButton(ctx){
                if (ctx.attr('state') == 'active') {
                    ctx.attr('state', 'inactive');
                    ctx.css('color', '#6c757d');
                    ctx.css('background-color', 'transparent');
                    ctx.css('border-color', '#6c757d;');
                }
                else{
                    ctx.attr('state', 'active');
                    ctx.css('color', '#fff');
                    ctx.css('background-color', '#6c757d');
                    ctx.css('border-color', 'rgb(108, 117, 125)');
                }
            }

            function formatString(str, ...params) {
                for (let i = 0; i < params.length; i++) {
                    var reg = new RegExp("\\{" + i + "\\}", "gm");
                    str = str.replace(reg, params[i]);
                }
                return str;
            }

            clockUpdate();
            setInterval(clockUpdate, 1000);
            function clockUpdate() {
                var date = new Date();
                $('.digital-clock').css({'color': '#2d6b86'});
                function addZero(x) {
                    if (x < 10) {
                        return x = '0' + x;
                    } else {
                        return x;
                    }
                }

                var d = addZero(date.getDate());
                var mo = addZero(date.getMonth() + 1);
                var y = date.getFullYear();
                var h = addZero(date.getHours());
                var m = addZero(date.getMinutes());
                var s = addZero(date.getSeconds());

                $('.digital-clock').text(d + "/" + mo + "/" + y + " " + h + ':' + m + ':' + s)
            }

            setInterval(getWeight, 500);
            function getWeight() {
                if($("#taring").attr('state') == 'active'){
                    var dataSend = JSON.stringify({"chkpoint_id" : $("#chkpName").attr("value"), "tare" : $('#tareValue').text()})
                }else if($("#taring").attr('state') == null || $("#taring").attr('state') == "inactive"){
                    var dataSend = JSON.stringify({"chkpoint_id" : $("#chkpName").attr("value")})
                }
                $.ajax({
                    url: '/fcd_weight_scale_mrp/getWeight',
                    type: 'POST',
                    contentType: 'application/json',
                    timeout: 5000,
                    data: dataSend
                }).done(function (data) {
                    if (!data.result.error && !data.error) {
                        if($("#taring").attr('name') == 'active'){
                            $('#weight').val(data.result.weight_value)
                        }else if($("#taring").attr('name') == null){
                            $('#weight').val(data.result.weight_value)
                        }
                    }
                    else{
                        console.log(data.result.error)
                    }
                }).fail(function (e) {
                    console.log("Impossible to connect with Odoo");
                });
            }
            //OnClick
            $('#taring').on('click', function() {
                tareStyleButton($(this));
                if ($(this).attr('state') == 'active') {
                    $('#tareValue').text($("#weight").val())
                }
                else{
                    $('#tareValue').text("0");
                }
                $("#myInputID").blur();
            });

            $("#endLot").on('click', function() {
                if ($("#lotSelect").val() != $("#txt_translate_select_lot").text()) {
                    $("#lotSure").text($("#lotSelect option:selected").text())
                    myModal.toggle();
                }
                else{
                    notifier.alert($("#txt_translate_alert_no_lot").text());
                }
                $("#myInputID").blur();
            });

            $('#yes').on('click', function(){
                var jsonSend = {
                    "stock_move_id": $("#lotSelect").val().split("/")[0],
                }
                jsonSend = JSON.stringify(jsonSend)          
                $.ajax({
                    url: '/fcd_weight_scale_mrp/endLot',
                    type: 'POST',
                    contentType: 'application/json',
                    data: jsonSend
                }).done(function (data) {
                    if (!data.result.error){
                        if($("#endLot").attr('state') == "active"){
                            loctactive_get();
                        }
                        notifier.success($("#txt_translate_lot_finished").text());
                    }
                    else {
                        notifier.alert(data.result.error);
                    }
                }).fail(function (e) {
                    console.log("Impossible to connect with Odoo");
                });
            });

            $('#package').on('click', function() {
                var jsonSend = {
                    "output_product_id" : $("#productSelect").val(),
                    "input_product_id" : $("#lotSelect").val().split("/")[1],
                    "stock_move_id": $("#lotSelect").val().split("/")[0],
                    "checkpoint_id": $("#chkpName").attr("value"),
                    "quantity" : $("#weight").val(),
                    "weight_quantity" : $("#weight").val(),
                    "secondary_uom_id" : $("#typeBoxSelect").val(),
                }
                if (validation()) {
                    if($("#chkboxFixed").is(':checked')){
                        jsonSend = JSON.stringify(Object.assign(jsonSend, {"quantity" : $("#fixedQuantity").val()}))
                    }
                    else{
                        jsonSend = JSON.stringify(jsonSend)
                    }
                    $.ajax({
                        url: '/fcd_weight_scale_mrp/packaging',
                        type: 'POST',
                        contentType: 'application/json',
                        data: jsonSend
                    }).done(function (data) {
                        if (!data.result.error){
                            var result = JSON.parse(data.result);
                            notifier.success(_t('It has been weighted correctly'))
                            if (!($("#chkboxLabel").is(':checked'))) {
                                notifier.async(asyncFunc(result[0]['log_id']), resp => notifier.info(), undefined, _t('Wait a moment, please...'));
                            }
                            //Set Log View
                            if ($('tbody').children().length >= 4) {
                                $('tbody').children()[0].remove()
                            }
                            var dateWeight = new Date();
                            var hours = dateWeight.getHours();
                            var min = dateWeight.getMinutes();
                            var seconds = dateWeight.getSeconds();
                            if (hours.toString().length < 2) {
                                hours = "0" + hours.toString();
                            }
                            if (min.toString().length < 2) {
                                min = "0" + min.toString();
                            }
                            if (seconds.toString().length < 2) {
                                seconds = "0" + seconds.toString();
                            }
                            var arraySplitted = $("#lotSelect option:selected").text().split("-");
                            arraySplitted.pop();
                            arraySplitted.pop();
                            var nameProduct = arraySplitted.join("-");
                            var weight = 0;
                            if ($('#chkboxFixed').is(':checked')) {
                                weight = $("#fixedQuantity").val();
                            }
                            else{
                                weight = $("#weight").val();
                            }
                            $("tbody").append(formatString("<tr><td>{0}:{1}:{2}</td><td class='overflowTd'>{3}</td><td>{4} KG</td></tr>", hours, min, seconds, nameProduct, weight));
                        }
                        else{
                            notifier.alert(data.result.error);
                        }
                        loctactive_get();
                    }).fail(function (e) {
                        console.log("Impossible to connect with Odoo")
                    });
                };
                $("#package").blur();
            });

            //OnChange
            $('#lotSelect').on('change', function() {
                old_lot = $("#lotSelect").val();

                var qty_pending = parseFloat($("#lotSelect option:selected").attr("quantity"));

                if (qty_pending == 0){
                    $("#lotSelect").addClass("lot_pending_warning");
                }else{
                    $("#lotSelect").removeClass("lot_pending_warning");
                }

                //Update family
                let family_id = $("#lotSelect option:selected").val().split("/")[2];
                if (family_id != "false" && $("#lotSelect option:selected").val() != $("#txt_translate_select_lot").text()) {
                    $("#familySelect option[value='" + family_id + "']").attr("selected", true);
                }
                else{
                    $("#familySelect option[value='" + -1 + "']").attr("selected", true);
                }
                old_family = family_id;

                //Update products
                if ($("#lotSelect" ).val() == $("#txt_translate_select_lot").text()) {
                    var defaultSelect = $("#txt_translate_select_product").text();
                    $("#productSelect  option").remove();
                    $("#productSelect").append('<option>' + defaultSelect + '</option>');
                }else{
                    if ($("#familySelect").val() == -1) {
                        $("#productSelect > option:nth-child(1)").attr("selected", true);
                    }
                    else{
                        product_get();
                        old_product = $("#lotSelect option:selected").val().split("/")[1];
                        $("#productSelect option[value='" + old_product + "']").attr("selected", true);
                    }
                }

                //Update Box Type
                if ($("#productSelect" ).val() == $("#txt_translate_select_product").text()) {
                    var defaultSelect = $("#txt_translate_select_type_box").text();
                    $("#typeBoxSelect  option").remove();
                    $("#typeBoxSelect").append('<option>' + defaultSelect + '</option>');
                }else{
                    box_type_get();
                    old_product = $("#lotSelect option:selected").val().split("/")[1];
                    let type_box_id = $("#productSelect option:selected").attr("typeBox");
                    if (type_box_id != "False"){
                        $("#typeBoxSelect option[value='" + type_box_id + "']").attr("selected", true);
                    }
                }



            });

            $('#familySelect').on('change', function() {
                old_family = $("#familySelect").val();
                //Update products
                if ($("#familySelect").val() == $("#txt_translate_select_family").text()) {
                    var defaultSelect = $("#txt_translate_select_product").text();
                    $("#productSelect  option").remove();
                    $("#productSelect").append('<option>' + defaultSelect + '</option>');
                }else{
                    product_get();
                }

            });

            $('#chkboxFixed').on('change', function() {
                if ($('#chkboxFixed').is(':checked')) {
                    $("#fixedQuantity").val("");
                }
            });

            $('#productSelect').on('change', function() {
                old_product = $("#productSelect").val();
                if ($("#productSelect").val() == $("#txt_translate_select_product").text()) {
                    var defaultSelect = $("#txt_translate_select_type_box").text();
                    $("#typeBoxSelect  option").remove();
                    $("#typeBoxSelect").append('<option>' + defaultSelect + '</option>');
                }else{
                    box_type_get();
                }
                let type_box_id = $("#productSelect option:selected").attr("typeBox");
                if (type_box_id != "False"){
                    $("#typeBoxSelect option[value='" + type_box_id + "']").attr("selected", true);
                }
            });

            //OnInput
            $('#fixedQuantity').on('input', function() {
                if ($('#fixedQuantity').val() != "" && $('#fixedQuantity').val() != "0") {
                    $('#chkboxFixed').prop('checked', true);
                }
                else{
                    $('#chkboxFixed').prop('checked', false);
                }
            });

            //OnKeyDown
            // $('#connectScale').keypress(function(e){
            //     e.preventDefault();
            // });
            // $('connectScale').mousedown(function(e) {
            //     e.stopImmediatePropagation(); //stops event bubbling
            //     e.preventDefault();  //stops default browser action (focus)
            // });

            document.body.onkeydown = function(e){
                if (e.keyCode != 190){
                    barcode_text += String.fromCharCode(e.keyCode)
                }else{
                    console.log("Completo: " + barcode_text)
                    $("#lotSelect option[lot='" + barcode_text + "']").attr("selected", true);

                    let qty_done = parseFloat($("#lotSelect option:selected").attr("quantity"));
                    if (qty_done <= 0) {
                        $("#lotSelect").addClass("lot_pending_warning");
                    }
                    else{
                        $("#lotSelect").removeClass("lot_pending_warning");
                    }
                    old_lot = $("#lotSelect").val();
                    barcode_text = ""

                    //Todo: Code repeated, make a function
                    //Update family
                    let family_id = $("#lotSelect option:selected").val().split("/")[2];
                    $("#familySelect option[value='" + family_id + "']").attr("selected", true);
                    old_family = family_id;

                    //Update products
                    if ($( "#lotSelect" ).val() == $("#txt_translate_select_lot").text()) {
                        var defaultSelect = $("#txt_translate_select_product").text();
                        $("#productSelect  option").remove();
                        $("#productSelect").append('<option>' + defaultSelect + '</option>');
                    }else{
                        product_get();
                        old_product = $("#lotSelect option:selected").val().split("/")[1]; 
                        $("#productSelect option[value='" + old_product + "']").attr("selected", true);
                    }
                }
            };

            loctactive_get();
            // GetData
            function loctactive_get () {
                try {
                    $.ajax({
                        url: '/fcd_weight_scale_mrp/lotactive',
                        type: 'POST',
                        contentType: 'application/json',
                        timeout: 4000,
                        data: JSON.stringify({"checkpoint_id": $("#chkpName").attr("value")})
                    }).done(function (data) {
                        if (!data.result.error){
                            var result = JSON.parse(data.result);
                            var defaultSelect = $("#txt_translate_select_lot").text();
                            $("#lotSelect  option").remove();
                            $("#lotSelect").append('<option>' + defaultSelect + '</option>');
                            for (var i = 0; i < result.length; i++) {
                                var qty_pending = (parseFloat(result[i]["qty_pending"])).toFixed(2);
                                var extra_style = ""
                                if (qty_pending <= 0){
                                    extra_style = "class='lot_pending_warning'";
                                    qty_pending = 0;
                                };

                                //Creation options
                                let optionValues = "'" + result[i]["move_id"] + "/" + result[i]["product_id"] + "/" + result[i]["family_id"] + "'";
                                let optionName = formatString("{0} - {1}", result[i]["product_name"], result[i]["lot_name"])
                                $("#lotSelect").append(formatString("<option quantity={0} lot={1} value={2} {3}>{4} ({5}Kg) </option>",
                                    qty_pending,
                                    result[i]["stock_production_lot_name"],
                                    optionValues,
                                    extra_style,
                                    optionName,
                                    qty_pending
                                )
                            )};
                            if ($('[value="' + old_lot + '"]').length > 0) {
                                $("#lotSelect").val(old_lot);
                            };
                            var qty_pending = parseFloat($("#lotSelect option:selected").attr("quantity"));

                            if (qty_pending == 0){
                                $("#lotSelect").addClass("lot_pending_warning");
                            }else{
                                $("#lotSelect").removeClass("lot_pending_warning");
                            }
                            window.setTimeout(loctactive_get, 5000);
                        }
                        else{
                            notifier.alert(data.result.error);
                            window.setTimeout(loctactive_get, 5000);
                        }
                    }).fail(function () {
                        loctactive_get();
                    });
                } catch (error) {
                    console.log("Impossible to connect with Odoo")
                }
            }

            function family_get() {
                try {
                    $.ajax({
                        url: '/fcd_weight_scale_mrp/familyget',
                        type: 'POST',
                        contentType: 'application/json',
                        async: false,
                        data: JSON.stringify({})
                    }).done(function (data) {
                        if (!data.result.error){
                            var result = JSON.parse(data.result);
                            var defaultSelect = $("#txt_translate_select_family").text();
                            $("#familySelect  option").remove();
                            $("#familySelect").append('<option value=-1>' + defaultSelect + '</option>');
                            for (var i = 0; i < result.length; i++) {
                                var value_family = Object.values(result[i])[0];
                                $("#familySelect").append('<option value="' + value_family + '">' + value_family + '</option>');
                            }
                            if ($('[value="' + old_family + '"]').length > 0) {
                                $("#familySelect").val(old_family)
                            }
                        }
                        else{
                            notifier.alert(data.result.error);
                        }
                        window.setTimeout(family_get, 5000);
                        if ($("#familySelect").val() != -1) {
                            product_get();
                        }

                    }).fail(function () {
                        window.setTimeout(family_get, 5000);
                        console.log("Impossible to connect with Odoo")
                    });
                } catch (error) {
                    console.log(error)
                }
            }
            family_get();

            function product_get() {
                try {
                    var jsonSend = {
                        "family_id" : old_family
                    }
                    $.ajax({
                        url: '/fcd_weight_scale_mrp/productget',
                        type: 'POST',
                        contentType: 'application/json',
                        async: false,
                        data: JSON.stringify({jsonSend})
                    }).done(function (data) {
                        if (!data.result.error){
                            var result = JSON.parse(data.result);
                            var defaultSelect = $("#txt_translate_select_product").text();
                            $("#productSelect  option").remove();
                            $("#productSelect").append('<option>' + defaultSelect + '</option>');
                            for (let i = 0; i < result.length; i++) {
                                if (result[i]["product_id"]) {
                                    $("#productSelect").append('<option typeBox="' + result[i]["type_box"] + '" value="' + result[i]["product_id"] + '">' + result[i]["product_name"] + '</option>');
                                }
                            }
                            if ($('#productSelect [value="' + old_product + '"]').length > 0) {
                                $("#productSelect").val(old_product)
                            }
                            return true;
                        }
                        else{
                            notifier.alert(data.result.error);
                        }
                    }).fail(function () {
                        console.log("Impossible to connect with Odoo")
                    });
                } catch (error) {
                    console.log(error)
                }
            }

            function box_type_get() {
                try {
                    var jsonSend = {
                        "product_id" : old_product
                    }
                    $.ajax({
                        url: '/fcd_weight_scale_mrp/boxtypeget',
                        type: 'POST',
                        contentType: 'application/json',
                        async: false,
                        data: JSON.stringify({jsonSend})
                    }).done(function (data) {
                        if (!data.result.error){
                            var result = JSON.parse(data.result);
                            var defaultSelect = $("#txt_translate_select_type_box").text();
                            $("#typeBoxSelect  option").remove();
                            $("#typeBoxSelect").append('<option>' + defaultSelect + '</option>');
                            for (let i = 0; i < result.length; i++) {
                                if (result[i][0]) {
                                    $("#typeBoxSelect").append('<option value="' + result[i][0] + '">' + result[i][1] + '</option>');
                                }
                            }
                            if ($('#typeBoxSelect [value="' + old_product + '"]').length > 0) {
                                $("#typeBoxSelect").val(old_product)
                            }
                        }
                        else{
                            notifier.alert(data.result.error);
                        }
                    }).fail(function () {
                        console.log("Impossible to connect with Odoo")
                    });
                } catch (error) {
                    console.log(error)
                }
            }
        }

    });
});
