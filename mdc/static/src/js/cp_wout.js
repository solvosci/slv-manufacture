// https://zer0.degree/chapter1/JavaScript-closure-and-design-patterns.html
var WoutState = /*(*/function () {

    var chkpoint_id = +$('#chkpoint_id').val();
    var card_categ_P_id = +$('#card_categ_P_id').val();
    var card_categ_L_id = +$('#card_categ_L_id').val();
    var card_categ_PC_id = +$('#card_categ_PC_id').val();

    var cards_in = [];
    var card_workstation = null;
    var quality_id = +$('#quality_select').val();
    /* var last_weight = 0; */

    var info = function (message, level) {
        show_info(message, level);
        // TODO more suff?
    }

    var currentLotId = function () {
        return (
            cards_in.length > 0 ?
            cards_in[0].win_lot_id :
            ''
        );
    }

    var inputCount = function () {
        return cards_in.length;
    }

    var isOneInput = function () {
        return $('#one_input_button').hasClass('enabled');
    }

    var isCrumbsMode = function () {
        return $('#crumbs_button').hasClass('enabled');
    }

    var isSharedMode = function () {
        return $('#shared_button').hasClass('enabled');
    }

    var addCard = function (card_data) {

        // 0.- If is first read, we must clear screen (that is currently showing last operation data)
        check_reset_screen();

        // 1.- Check card_categ
        console.log('Checking card category ' + card_data.card_categ_id + '...');
        // 2.- Check data saving

        if ( (card_data.card_categ_id === card_categ_P_id) || (card_data.card_categ_id === card_categ_PC_id) ) {
            var bProductCard = (card_data.card_categ_id === card_categ_P_id);
            // Product card received
            if ( (inputCount() === 2) || isCrumbsMode() ) {
                // Too many product cards or crumbs mode is selected
                throw new Error(
                    $('#t_chkpoint_wout_input_workstation_expected_err').html()
                        .format(card_data.card_code)
                );
            }
            if ( (inputCount() === 1) && isOneInput() ) {
                // Second input card when one input mode is set
                throw new Error(
                    $('#t_chkpoint_wout_input_one_input_already_selected_err').html()
                        .format(card_data.card_code)
                );
            }
            if ( (inputCount() === 1) && (card_data.card_code === cards_in[0].card_code) ) {
                // Repeated card
                throw new Error(
                    $('#t_chkpoint_wout_input_repeated_err').html()
                        .format(card_data.card_code)
                );
            }
            if ( bProductCard && !('win_weight' in card_data) ) {
                // Product card with no data associated
                throw new Error(
                    $('#t_chkpoint_wout_input_no_input_err').html()
                        .format(card_data.card_code)
                );
            }
            var lotId = currentLotId();
            if ( !bProductCard && !('win_lot_id' in card_data) && !lotId ) {
                // Joker card with no lot associated and lot is not yet determined
                throw new Error(
                    $('#t_chkpoint_wout_jc_no_lot_err').html()
                        .format(card_data.card_code)
                );
            }
            if ( lotId && card_data.win_lot_id && (lotId != card_data.win_lot_id) ) {
                // Product/Joker card associated to a different lot
                throw new Error(
                    $('#t_chkpoint_wout_input_lot_err').html()
                        .format(card_data.card_code, card_data.win_lot_name)
               );
            }

            // Product/Joker card is allowed
            cards_in.push(card_data);
            // - Too late for set one input mode
            if  ( cards_in.length == 2 ) {
                $('#one_input_button').prop('disabled', true);
            }
            // - Too late for crumbs mode
            $('#crumbs_button').prop('disabled', true);

            $('#lot').html(card_data.win_lot_name);
            $('#card_in_' + cards_in.length).val(
                bProductCard ?
                '{0} {1}'.format(card_data.win_weight, card_data.win_uom) :
                $('#t_chkpoint_wout_jc_description').html()
            );

            info($('#t_chkpoint_wout_input_jc_added').html().format(card_data.card_code), 'ok');
        }
        else if ( card_data.card_categ_id === card_categ_L_id ) {
            // Workstation card received
            if ( (inputCount() === 0) && !isCrumbsMode() && !isSharedMode() ) {
                // Workstation card is not allowed when no input data is present (but crumbs and shared mode)
                throw new Error(
                    $('#t_chkpoint_wout_workstation_input_expected_err').html()
                        .format(card_data.card_code)
                );
            }
            if ( (inputCount() === 1) && !isOneInput() && !isSharedMode() ) {
                // Workstation card is not allowed when only one input present (only in "one input" mode or shared mode)
                throw new Error(
                    $('#t_chkpoint_wout_workstation_input_expected_err').html()
                        .format(card_data.card_code)
                );
            }

            if ( !('workstation' in card_data) ) {
                throw new Error(
                    $('#t_chkpoint_wout_workstation_no_workstation_err').html()
                        .format(card_data.card_code)
                );
            }

            // Workstation card is allowed: fire saving data
            card_workstation = card_data;
            $('#card_workstation').val(card_data.workstation);
            $('#last_quality').val($('#quality_select option:selected').text().trim());
            console.log(`Added workstation Card #${card_data.card_code}. Saving...`)
            save();
            return;
        }
        else {
            throw new Error(
                $('#t_chkpoint_wout_invalid_card_err').html()
                    .format(card_data.card_code)
            );
        }

    }

    var updateQuality = function () {
        quality_id = $('#quality_select').val();
    }

    var save = function () {

        $.ajax({
            url: '/mdc/cp/wout/' + chkpoint_id + '/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cards_in: cards_in,
                card_workstation: card_workstation,
                quality_id: quality_id,
                shared: isSharedMode(),
                wout_categ_code: (
                    isCrumbsMode() ?
                    'SP1' : 'P'
                )
            })
        }).done(function (data) {
            try {
                console.log(data.result);
                if ( data.result.err ) {
                    throw new Error($('#t_chkpoint_wout_save_err').html().format(data.result.err));
                }
                else {
                    displayUpdate(data.result);
                    reset();
                    return;
                }
            }
            catch (e) {
                info(e.message, 'err')
                reset();
            }
        }).fail(function () {
            info($('#t_chkpoint_wout_save_err_unknown').html(), 'err');
            reset();
        });

    }

    var displayUpdate = function (data) {
        $('#last_weight').val(data.weight + ' ' + data.w_uom);
        $('#card_in_1,#card_in_2,#card_workstation,#last_weight,#last_quality')
            .removeClass('failed').addClass('success');
        info($('#t_chkpoint_wout_save_ok').html(), 'ok')
        window.setTimeout(function () {
                $('#card_in_1,#card_in_2,#card_workstation,#last_weight,#last_quality').removeClass('success');
            },
            3000
        );
    }

    var reset = function () {
        cards_in = [];
        card_workstation = null;
        $('#quality_select').val($('#initial_quality_id').val()).change();
        if ( isOneInput() )  switch_enabled($('#one_input_button'), false);
        if ( isCrumbsMode() )  switch_enabled($('#crumbs_button'), false);
        if ( isSharedMode() )  switch_enabled($('#shared_button'), false);
        $('#one_input_button,#crumbs_button,#shared_button').prop('disabled', false);
    }

    var check_reset_screen = function () {
        if ( inputCount() === 0  && (card_workstation === null) ) {
            $('#lot').html('');
            $('#card_in_1,#card_in_2,#card_workstation,#last_weight,#last_quality').val('');
        }
    }

    return {
        addCard: addCard,
        updateQuality: updateQuality
    }

}/*)()*/;

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
            show_info('Read card #' + obj.Event.user_id.user_id, 'ok');
            read_card_manage(obj.Event.user_id.user_id);
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        show_info('ERROR: ' + e.message, 'err');
    }

}

ws_event_open = function () {
    console.log('WOUT ws open!!!');
    show_info($('#t_ws_rfid_onopen_ready').html(), 'ok');
}

read_card_manage = function (card_code) {

    $.ajax({
        url: '/mdc/cp/carddata/' + card_code,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({})
    }).done(function (data) {
        try {
            console.log(data.result);
            if ( data.result.err ) {
                throw new Error('ERROR retrieving card data: ' + data.result.err);
            }
            else {
                woutState.addCard(data.result);
                return;
            }
        }
        catch (e) {
            show_info(e.message, 'err');
            save_log({ 'error':  e.message, 'chkpoint_id': $('#chkpoint_id').val() })
        }
    }).fail(function () {
        show_info('ERROR retrieving card data (unknown)', 'err');
    });

}

quality_edit = function(delta) {
    var sel_count = $('#quality_select > optgroup > option').length
    var current_index = $('#quality_select').prop('selectedIndex');
    var next_index = current_index + delta;
    if ( next_index < 0)  next_index = 0;
    if ( next_index >= sel_count )  next_index = sel_count - 1;
    if ( next_index != current_index ) {
        $('#quality_select').prop('selectedIndex', next_index).change();
    }
}

var woutState = null;

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received, { 'onopen_function': ws_event_open });
    show_info($('#t_ws_rfid_onopen_wait').html(), 'ok');

    // TODO additional initial stuff

    // Button events
    $('#quality_up_button').click(function () {
        quality_edit(1);
    });
    $('#quality_down_button').click(function () {
        quality_edit(-1);
    });
    $('#one_input_button,#crumbs_button,#shared_button').click(function () {
        switch_enabled(this, true);
        save_log({ 'click_id':  this.id, 'chkpoint_id': $('#chkpoint_id').val() })
    });
    // - Crumbs and shared mode are incompatible
    $('#shared_button').click(function () {
        $('#crumbs_button').prop('disabled', true);
    });
    $('#crumbs_button').click(function () {
        $('#shared_button').prop('disabled', true);
    });

    woutState = WoutState();

    $('#quality_select')
        .change(woutState.updateQuality)
        .val($('#initial_quality_id').val())
        .change();

    // Simulation support
    if ( $('#ws_simul').val().toLowerCase() === 'true' ) {
        $('#card_in_simul').change(function () {
            if ( $(this).val() )  read_card_manage($(this).val());
        });
        $('#rfid_simul_data').show();
    }

});
