$(".grievance-btn").click(function () {
    var url = $(this).data("url");
    $.ajax({
        url: url,
        success: function (data) {
            $("#grivance-details").empty();
            $("#grivance-details").html(data);
            $('#grievanceModal').modal('toggle');
        }
    });
});
$(document).on('click', '#grievance-reply-submit', function(event){
    var frm = $('#grievance-reply-form');
    $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (data) {
                $("#grivance-details").empty();
                $("#grivance-details").html(data);
            },
            error: function (data) {
                console.log('An error occurred.');
                console.log(data);
            },
        });
});