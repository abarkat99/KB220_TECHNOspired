let $id_sub_category = $("#id_sub_category");
let $submit_grievance = $(".submit_grievance");
let $id_category = $("#id_category");
function get_subcategories() {
    let url = $(".form-loads-subcategories").data("sub-categories-url");
    let category = $id_category.val();
    $.ajax({
        url: url,
        data: {
            'category': category
        },
        success: function (data) {
            $id_sub_category.html(data);
            $id_sub_category.removeAttr("disabled");
            $submit_grievance.removeAttr("disabled");
        },
        error: function () {
            $id_sub_category.children().not(':first-child').remove();
            $id_sub_category.attr("disabled", true);
            $submit_grievance.attr("disabled", true);
        }
    });
}
if ($id_category.val() == '') {
    $id_sub_category.attr("disabled", true);
    $submit_grievance.attr("disabled", true);
}
$id_category.change(function () {
    get_subcategories();
});