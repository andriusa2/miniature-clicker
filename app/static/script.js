function submit(id) {
    $("#voting").val(id);
    $("#form").submit();
}

$(document).ready(
    function(){
        $(".flashes").delay(5000).fadeOut(500);
    });