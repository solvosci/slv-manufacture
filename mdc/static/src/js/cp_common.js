page_reload = function () {
    window.location.reload(true);
}

save_log = function (logdata) {

    $.ajax({
        url: '/mdc/cp/log',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(logdata)
    }).done(function (data) {
        // Does nothing
        console.log(data);
    }).fail(function () {
        // Does nothing
        console.log(data);
    });

}

show_info = function (message, level) {

    $('#info_div')
        .removeClass('info_div_ok info_div_err')
        .addClass('info_div_' + level)
        .html(message);

}

ws_create = function (onmessage_function, other_funcs) {

    // TODO uncomment this for testing purposes
    // return false;
    if ( $('#ws_simul').val().toLowerCase() === 'true' )  return;

    other_funcs = (other_funcs || {});

    var sessionId = $('#ws_session_id').val();
    var ws = new WebSocket($('#ws_wsapi_url').val());

    ws.onopen = function(){
        console.log('WebSocket opened');
        ws.send('bs-session-id' + "=" + sessionId);
        if ( other_funcs.onopen_function && (typeof other_funcs.onopen_function === 'function') ) {
            other_funcs.onopen_function();
        }
    };

    ws.onmessage = onmessage_function;

    // TODO onerror

    return ws;

}

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

switch_enabled = function (obj, force_readonly) {
    if ( $(obj).hasClass('enabled') ) {
        $(obj).removeClass('enabled').addClass('disabled');
    }
    else {
        $(obj).removeClass('disabled').addClass('enabled');
    }
    $(obj).prop('disabled', force_readonly);
}

$(document).ready(function () {

    $('#reload_button').click(function () {
        page_reload();
    });

});