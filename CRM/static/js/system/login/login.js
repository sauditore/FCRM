/**
 * Created by saeed on 5/4/16.
 */

$(function(){
    $('form').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/login/',
            method: 'post',
            data: $(this).serialize(),
            success: function(){
                document.location = '/'
            },
            error: function(er){
                post_error(er);
            }
        })
    });
});
