ws_event_open = function () {
    console.log('Card registration ws open!!!');
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
            show_info('Read card #' + $('#card_read_input').val(), 'ok');
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        show_info('ERROR: ' + e.message, 'err');
    }

}

card_register_click = function () {

    try {
        if ( !$('#device_select').val() ) {
            // TODO translate
            throw new Error('there is no device selected');
        }
        if ( !$('#card_categ_select').val() ) {
            // TODO translate
            throw new Error('there is no card category selected');
        }
        if ( !$('#card_read_input').val() ) {
            // TODO translate
            throw new Error('first slide a card');
        }

        var data = {
            'card_code': parseInt($('#card_read_input').val()),
            'card_categ_id': parseInt($('#card_categ_select').val(), 10),
            'employee_id': parseInt($('#employee_select').val(), 10),
            'workstation_id': parseInt($('#workstation_select').val(), 10)
        }

        // TODO translate
        $('#info_div')
            .removeClass('info_div_err').addClass('info_div_ok')
            .html('Registering card... ');
        $.ajax({
            url: '/mdc/cp/cardreg/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function (data) {
            console.log(data.result);
            if ( data.result.err ) {
                show_info('ERROR ' + data.result.err, 'err');
            }
            else {
                // TODO translate
                show_info('Card #' + $('#card_read_input').val() +
                        ' successfully registered with id ' + data.result.card_id, 'ok');
            }
        }).fail(function () {
            // TODO translate
            show_info('ERROR registering card (unknown)', 'err');
        });
    }
    catch (e) {
        // TODO translate?
        show_info('ERROR: ' + e.message, 'err');
    }

}

$(document).ready(function() {

    $('#confirm_button').click(card_register_click);

    // TODO error handling

    /* var ws = */ws_create(ws_event_received, { 'onopen_function': ws_event_open });
    show_info($('#t_ws_rfid_onopen_wait').html(), 'ok');

});