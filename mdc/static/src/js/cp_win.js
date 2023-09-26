ws_event_open = function () {
    console.log('WIN ws open!!!');
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

        if ( $('#rfid_reader_code').val() === obj.Event.device_id.id ) {
            console.log('Matched!');
            show_info($('#t_chkpoint_win_read_card').html().format(obj.Event.user_id.user_id), 'ok');
            data_win_save({
                'card_code': obj.Event.user_id.user_id
            });
            return;
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        show_info('ERROR: ' + e.message, 'err');
    }

}

loctactive_get_schedule = function () {

    window.setTimeout(
        loctactive_get,
        5*1000
    );

}

loctactive_get = function () {

    $.ajax({
        url: '/mdc/cp/win/' + $('#chkpoint_id').val() + '/lotactive',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({})
    }).done(function (data) {
        console.log(data.result);
        if ( data.result.err ) {
            show_info($('#t_chkpoint_win_lot_err').html().format(data.result.err), 'err');
            // TODO additional stuff over display
        }
        else {
            $('#lot').html(data.result.lotactive);
        }
        loctactive_get_schedule();
    }).fail(function () {
        show_info($('#t_chkpoint_win_lot_err_unknown').html(), 'err');
        loctactive_get_schedule();
    });

}

data_win_save = function (data) {

    $.ajax({
        url: '/mdc/cp/win/' + $('#chkpoint_id').val() + '/save',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data)
    }).done(function (data) {
        console.log(data.result);
        if ( data.result.err ) {
            show_info('ERROR: ' + data.result.err, 'err');
            $('#last_weight').val('')
                .removeClass('success').addClass('failed');
            window.setTimeout(function () { $('#last_card_read,#last_weight').removeClass('failed'); }, 3000);
        }
        else {
            show_info($('#t_chkpoint_win_save_ok').html(), 'ok');
            $('#lot').html(data.result.lotactive)
            // $('#last_card_read').val(data.result.card_code).addClass('success');
            $('#last_weight').val(data.result.weight + ' ' + data.result.w_uom)
                .removeClass('failed').addClass('success');
            window.setTimeout(function () { $('#last_card_read,#last_weight').removeClass('success'); }, 3000);
        }
    }).fail(function () {
        show_info($('#t_chkpoint_win_save_err_unknown').html(), 'err');
    });

}

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received, { 'onopen_function': ws_event_open });
    show_info($('#t_ws_rfid_onopen_wait').html(), 'ok');

    // Simulation support
    if ( $('#ws_simul').val().toLowerCase() === 'true' ) {
        $('#last_card_read').change(function () {
            if ( $(this).val() )  data_win_save({'card_code': $(this).val()});
        });
        $('#rfid_simul_data').show();
    }


    loctactive_get();

});
