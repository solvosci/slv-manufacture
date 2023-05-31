function closeAlert(){
    $('#alert').addClass('d-none').removeClass('show');
};
function closeAlert2(){
    $('#alert2').addClass('d-none').removeClass('show');
};
function closeAlert3(){
    $('#alert3').addClass('d-none').removeClass('show');
};
function closeAlert4(){
    $('#alert4').addClass('d-none').removeClass('show');
};
function closeAlert5(){
    $('#alert5').addClass('d-none').removeClass('show');
};

// $(document).ready(function () {
$('#initialize').ready(function () {

    //Guardar datos iniciales
    var totalPricelists2 = $("tbody .priceList").length / $(".chkb").length;
    var totalCheckbox =  $(".chkb").length;
    var totalPricelists = $("tbody .priceList");
    var matrizTarifasIniciales = new Array(totalCheckbox);
    var contador = 0;
    for (let i = 0; i < totalCheckbox; i++) {
        matrizTarifasIniciales[i] = new Array(totalPricelists2);
        for (let ii = 0; ii < totalPricelists2; ii++) {
            matrizTarifasIniciales[i][ii] = parseFloat(totalPricelists[contador].innerText).toFixed(2);
            contador++;
        }
    }

    //First Load
    $('#alert').addClass('d-none').removeClass('show');
    $('#alert2').addClass('d-none').removeClass('show');
    $('#alert3').addClass('d-none').removeClass('show');
    $('#alert4').addClass('d-none').removeClass('show');
    $('#alert5').addClass('d-none').removeClass('show');
    $('#loading').addClass('d-none');
    $('#loading').removeClass('d-flex');
    $('.o_cp_controller').removeClass('d-none');
    $('.o_content').removeClass('d-none');

    //Set table width points automáticamente
    if (totalPricelists2 > 10) {
        x = (totalPricelists2 - 11) * 100;
        x = x + $("table").width();
        $("table").css("width", x)
    }

    //Set move with arrow directions
    $("td").keydown(function (event) {  //Get key press
        if (event.keyCode == 37) { //Left arrow
            if (this.previousElementSibling.getAttribute("contenteditable")) {
                this.previousElementSibling.focus();
            }
            else if (this.previousElementSibling.previousElementSibling.previousElementSibling.getAttribute("contenteditable")) {
                this.previousElementSibling.previousElementSibling.previousElementSibling.focus();
            }
        }
        else if (event.keyCode == 38) { //Up arrow
            let cell = this.cellIndex;
            this.parentElement.previousElementSibling.cells[cell].focus();
        }
        else if (event.keyCode == 39) { // Right arrow
            if (this.nextElementSibling.getAttribute("contenteditable")) {
                this.nextElementSibling.focus();
            }
            else if (this.nextElementSibling.nextElementSibling.nextElementSibling.getAttribute("contenteditable")) {
                this.nextElementSibling.nextElementSibling.nextElementSibling.focus();
            }
        }
        else if (event.keyCode == 40) { //Down arrow
            let cell = this.cellIndex;
            this.parentElement.nextElementSibling.cells[cell].focus();
        }
    });

    $("#dateTime").val(new Date().toISOString().slice(0, 10));

    $(".pricelist").each(function( index ) {
        if ($(".pricelist")[index].innerText != '' && $(".pricelist")[index].innerText != "\n") {
            $(".pricelist")[index].innerText = parseFloat($(".pricelist")[index].innerText).toFixed(2);
        }
    });

    $('.chkb1').on("click", function () {
        var totalChk = $(".chkb");
        [].forEach.call(totalChk, function (el) {
            if (document.getElementsByName("chk1")[0].checked == false) {
                el.checked = false;
            }
            else {
                el.checked = true;
            }
        });
    });

    $('.pricelist').on("input", function () {
        let tryLetter = false;
        if ($.isNumeric(this.innerText) || this.innerText == "." || this.innerText == "\'" || this.innerText == "") {
            checkIfOld(this);
        }
        else {
            if (this.innerText.length > 0) {
                this.innerText = '';
                checkIfOld(this);
            }
        }
    });

    $('#btnGuardar').on("click", function () {
        var matrizEnviar = [];
        var matrizTemp = document.getElementsByClassName("changed");
        if (matrizTemp.length > 0) {
            if ($("#dateTime").val() != '') {
                [].forEach.call(matrizTemp, function (el) {
                    matrizEnviar.push({ "pricelist_id": el.id, "product_tmpl_id": el.getAttribute("name"), "fixed_price": el.innerText, "date_start": $("#dateTime").val() });
                });
                console.log(matrizEnviar);
                new_array = {"data": matrizEnviar};
                console.log(new_array);
                $.ajax({
                    url: '/pricelist/items/get',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(new_array)
                }).done(function (data) {
                    $('#alert3').removeClass('d-none').addClass('show');
                    setTimeout(window.location.reload.bind(window.location), 2000);
                });
            }
            else{
                $('#alert4').removeClass('d-none').addClass('show');
            }
        }
        else{
            $('#alert5').removeClass('d-none').addClass('show');
        }
    });

    function increment() {
        var totalPriceList = $("tbody .priceList").length / $(".chkb").length;
        let numSumar = parseFloat(document.getElementById("inputIncrement").value);
        var totalChk = $(".chkb");
        var count = 0;

        [].forEach.call(totalChk, function (el) {
            if (el.checked == true) {
                [].forEach.call(el.parentElement.parentElement.children, function (element2) {
                    if (element2.classList.contains('pricelist')) {
                        if ($.isNumeric(element2.innerText)) {
                            element2.innerText = (parseFloat(parseFloat(element2.innerText) + parseFloat(numSumar))).toFixed(2);
                            checkIfOld(element2);
                        }
                    }
                    count++;
                });
            }
        });
        if (count == 0) {
            $('#alert2').removeClass('d-none').addClass('show');
        }
    }

    function incrementIn(numSum, trs) {
        var totalPriceList = $("tbody .priceList").length / $(".chkb").length;
        let numSumar = parseFloat(numSum);
        var totalChk = $(".chkb");
        if ($.isNumeric(numSumar)) {
            [].forEach.call(trs.children, function (element2) {
                if (element2.classList[0] == 'pricelist') {
                    if (element2.innerText != '' && element2.innerText != "\n") {
                        element2.innerText = (parseFloat(parseFloat(element2.innerText) + parseFloat(numSumar))).toFixed(2);
                        checkIfOld(element2);
                    }
                }
            });
        }
        else {
            $('#alert').removeClass('d-none').addClass('show');
        }
    }

    function setIn(numSet, trs) {
        var totalPriceList = $("tbody .priceList").length / $(".chkb").length;
        let numSumar = parseFloat(numSet);
        var totalChk = $(".chkb");

        if ($.isNumeric(numSumar)) {
            [].forEach.call(trs.children, function (element2) {
                if (element2.classList[0] == "pricelist") {
                    if (element2.innerText != '' && element2.innerText != "\n") {
                        element2.innerText = (parseFloat(numSumar)).toFixed(2);
                        checkIfOld(element2);
                    }
                }
            });
        }
        else {
            $('#alert').removeClass('d-none').addClass('show');
        }
    }

    function setValue() {
        var totalPriceList = $("tbody .priceList").length / $(".chkb").length;
        let numSet = parseFloat(document.getElementById("inputApply").value);
        var totalChk = $(".chkb");
        var count2 = 0;

        [].forEach.call(totalChk, function (el) {
            if (el.checked == true) {
                [].forEach.call(el.parentElement.parentElement.children, function (element2) {
                    if (element2.classList[0] == 'pricelist') {
                        if (element2.innerText != '' && element2.innerText != "\n") {
                            element2.innerText = (parseFloat(numSet)).toFixed(2);
                            checkIfOld(element2);
                        }
                    }
                });
                count2++;
            }
        });
        if (count2 == 0) {
            $('#alert2').removeClass('d-none').addClass('show');
        }
    }

    function checkIfOld(elemento){
        let exist = false;
        let contador = 0;
        var totalPricelists2 = $("tbody .priceList").length / $(".chkb").length;
        var totalCheckbox = $(".chkb").length;
        var totalPricelists = $("tbody .priceList");

        var nodes = Array.prototype.slice.call($('.pricelist'));
        nodes.indexOf(elemento);

        forTestStart:
        for (let i = 0; i < totalCheckbox; i++) {
            for (let ii = 0; ii < totalPricelists2; ii++) {
                if (contador == nodes.indexOf( elemento )) {
                    if (matrizTarifasIniciales[i][ii] == elemento.innerText) {
                        exist = true;
                    }
                    else if (elemento.innerText == '' && matrizTarifasIniciales[i][ii] == "NaN") {
                        exist = true;
                    }
                    break forTestStart;
                }
                contador++;
            }
        }
        if (!exist) {
            elemento.style.setProperty("background-color", "rgb(219, 219, 255)", "important");
            elemento.classList += " changed";
        }
        else{
            elemento.style.background = "none";
            elemento.classList.remove("changed")
        }
        return;
    }

    $('#increment').on("click", function () {
        if ($("#inputIncrement").val() == "" || $("#inputIncrement").val() == null) {
        }
        else { increment() }
    });
    $('#select_all').on("click", function () {
        [].forEach.call($(".chkb"), function (el) {
            if (!el.checked) {
                el.checked = true;
            }
        });
    });
    $('#unselect_all').on("click", function () {
        [].forEach.call($(".chkb"), function (el) {
            if (el.checked) {
                el.checked = false;
            }
        });
    });
    $('#newValue').on("click", function () {
        if ($("#inputApply").val() == "" || $("#inputApply").val() == null) {
        }
        else { setValue() }
    });

    $(".setIncrement").keypress(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            this.parentElement.firstElementChild.firstChild.checked = true;
            incrementIn(this.textContent, this.parentElement);
        }
    });

    $(".setValue").keypress(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            this.parentElement.firstElementChild.firstChild.checked = true;
            setIn(this.textContent, this.parentElement);
        }
    });

    $('.pricelist').keypress(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });

    $('#select_all').on("click", function () {
        [].forEach.call($(".chkb"), function (el) {
            if (!el.checked) {
                el.checked = true;
            }
        });
    });

    $('#unselect_all').on("click", function () {
        [].forEach.call($(".chkb"), function (el) {
            if (el.checked) {
                el.checked = false;
            }
        });
    });

});
