function submit(id) {
    $("#voting").val(id);
    $("#form").submit();
}

setTimeout('$(".flashes").hide()', 5000)