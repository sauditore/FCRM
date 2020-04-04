/**
 * Created by saeed on 5/4/16.
 */

$(function(){
    $('form').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/login/forget/',
            method: 'post',
            data: $(this).serialize(),
            success: function(){
                sAlert('نام کاربری و رمز عبور با موفقیت پیامک گردید. جهت ورود تایید را انتخاب کنید', 2, function(){
                    document.location = '/login/?skip=1';
                })
            },
            error: function(er){
                post_error(er);
            }
        });
    });
});
