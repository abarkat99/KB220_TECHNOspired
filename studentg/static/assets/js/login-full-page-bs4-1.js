$(function(){
    let prevImage = "user-icon.jpg";
    $("#login-username").on('blur', function(){
        let d = $(this).val();
        if (!d) {
            animateNewAvatar("user-icon.jpg");
            return;
        }
        d = gravatar(d, {size: 200});
        animateNewAvatar(d);
    });
    
    function animateNewAvatar(d) {
        const avatar = $(".login-user-avatar");
        if(d === prevImage) {
            return;
        }
        prevImage = d;
        avatar.addClass("backface");
        setTimeout(()=>{
            avatar.css({backgroundImage: `url("${d}")`});
            setTimeout(()=>{
                avatar.removeClass("backface");
            }, 200)
        }, 500);
    }
})