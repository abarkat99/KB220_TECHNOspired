$("#id_sub_category").attr("disabled", true);
$("#submit_grievance").attr("disabled", true);
$("#id_category").change(function () {
    var url = $("#grievance_form").attr("sub-categories-url");
    var category = $(this).val();
    $.ajax({
        url: url,
        data: {
            'category': category
        },
        success: function (data) {
            $("#id_sub_category").html(data);
            $("#id_sub_category").removeAttr("disabled");
            $("#submit_grievance").removeAttr("disabled");
        },
        error: function () {
            $("#id_sub_category").attr("disabled", true);
            $("#submit_grievance").attr("disabled", true);
        }
    });
});