/**
 * Created by saeed on 5/6/16.
 */

$(function(){
    $('form').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/login/register/',
            method: 'post',
            data: $(this).serialize(),
            success: function(){
                sAlert('درخواست شما با موفقیت ثیت گردید. با تشکر', 2, function(){
                    document.location = 'http://faratar.net'
                });
            },
            error: function(er){
                post_error(er);
            }
        })
    });
});

