$(document).ready(function() {
    loctactive_get_schedule = function () {
        window.setTimeout(
            loctactive_get,
            5*1000
        );
    }
    
    loctactive_get = function () {
        try {
            $.ajax({
                url: '/weight_scale/cp/lotactive', 
                // $('#chkpoint_id').val() Revisar obtención de Checkpoint
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({})
            }).done(function (data) {
                console.log(data.result);
                console.log(data);
                loctactive_get_schedule();
            }).fail(function () {
                loctactive_get_schedule();
            });
        } catch (error) {
            print(error)
        }
    
    }
    loctactive_get;
    $('#a').on('click', function() {
        $.ajax({
            url: '/weight_scale/cp/lotactive', 
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({})
        }).done(function (data) {
            data = JSON.parse(data.result)
            for (var key in data) {
                if(!key.endsWith("code")){
                    if (data.hasOwnProperty(key)) {
                        $("#dropwdown_lots").append('<option value="' + key + '">' + data[key] + ' - ' + data[key + "code"] + '</option>')
                    }
                }
            }
        }).fail(function (e) {
            console.log(e);
            alert("mal")
        });
    });
});