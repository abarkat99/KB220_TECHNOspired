$(document).ready(function() {
    var placeholder = "";
    $("input, label").on("mouseenter touchstart", function() {
        $(this).parent().find("input").focus();
        $(this).parent().find("label").css("top","25px").css("color","rgb(51,51,51)").css("font-size", "18px").css("padding-bottom","auto");
    });
    $("input, label").on("mouseleave",function() {
        $(this).parent().find("input").blur();
        if (!$(this).val()) {
            $(this).parent().find("label").css("top","53px").css("color","#999").css("font-size","18px").css("padding-bottom","0px");
        }
    });
    
    $("input").on("blur", function() {
        if (!$(this).val()) {
            $(this).parent().find("label").css("top","53px").css("color","#999").css("font-size","18px").css("padding-bottom","0px");
        }
    })
});