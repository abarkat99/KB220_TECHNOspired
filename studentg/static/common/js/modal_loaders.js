$('.view-message-btn').click(function () {
    $.ajax({
        url: $(this).data('url'),
        success: function (data) {
            $('#grievance-messages-modal').find('.modal-content').html(data);
            $('#grievance-messages-modal').modal('toggle');
        },
        error: function () {
            alert('Something Went Wrong!');
        }
    });
});