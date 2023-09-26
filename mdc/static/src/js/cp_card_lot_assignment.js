ws_event_open = function () {
    console.log('Card lot assignment ws open!!!');
    show_info($('#t_ws_rfid_onopen_ready').html(), 'ok');
}

ws_event_received = function (event) {

    try {
        console.log('Event received:');
        console.log(event.data);

        var obj = JSON.parse(event.data);

        if ( !(obj.Event && obj.Event.device_id && obj.Event.user_id) ) {
            console.log('Event not recognized');
            return;
        }

        console.log('Device: ' + obj.Event.device_id.id);
        console.log('Card/User: ' + obj.Event.user_id.user_id);

        var device = $('#device_select').val();
        if ( device && (device == obj.Event.device_id.id) ) {
            console.log('Matched!');
            $('#card_read_input').val(obj.Event.user_id.user_id);
            show_info($('#t_cardlot_card_info').html().format($('#card_read_input').val()), 'ok');
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        show_info('ERROR: ' + e.message, 'err');
    }

}

card_assign_lot_click = function () {

    try {
        if ( !$('#device_select').val() ) {
            throw new Error($('#t_cardlot_device_err').html());
        }
        if ( !$('#lot_select').val() ) {
            throw new Error($('#t_cardlot_lot_err').html());
        }
        if ( !$('#card_read_input').val() ) {
            throw new Error($('#t_cardlot_slide_err').html());
        }

        var data = {
            'card_code': parseInt($('#card_read_input').val()),
            'lot_id': parseInt($('#lot_select').val(), 10)
        }

        show_info($('#t_cardlot_card_waiting').html(), 'ok');
        $.ajax({
            url: '/mdc/cp/cardlot/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function (data) {
            console.log(data.result);
            if ( data.result.err ) {
                show_info('ERROR ' + data.result.err, 'err');
            }
            else {
                show_info($('#t_cardlot_success').html()
                    .format($('#card_read_input').val(), data.result.lot_name), 'ok');
            }
        }).fail(function () {
            show_info($('#t_cardlot_err_unknown').html(), 'err');
        });
    }
    catch (e) {
        show_info('ERROR: ' + e.message, 'err');
    }

}

$(document).ready(function() {

    $('#confirm_button').click(card_assign_lot_click);

    // TODO error handling

    /* var ws = */ws_create(ws_event_received, { 'onopen_function': ws_event_open });
    show_info($('#t_ws_rfid_onopen_wait').html(), 'ok');

});