$(".grievance-btn").click(function () {
    var url = $(this).attr("token-url");
    $.ajax({
        url: url,
        success: function (data) {
            $("#grivance-details").empty();
            $("#grivance-details").html(data);
            $('#grievanceModal').modal('toggle');
        }
    });
});