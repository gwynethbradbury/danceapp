$("#delete-event").click(function() {
    http_delete($(this));
    return false;
});

$("#delete-storyline").click(function() {
    http_delete($(this));
    return false;
});

function http_delete(element) {
    $.ajax({
        url: element.attr('href'),
        type: 'DELETE',
        success: function(result) {
            window.location.href = result;
        }
    });
}
