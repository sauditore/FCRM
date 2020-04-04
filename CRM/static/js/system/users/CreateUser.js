/**
 * Created by saeed on 4/6/16.
 */
$(function(){
    var fCreate = $('form[method="post"]');
    $('#bRandomUser').on('click', function(){
        $.ajax({
            url: "/ajax/?a=g",
            success: function(d){
                $('[name=u]').val(d).trigger('change');
            },
            error: function(er){

            }
        });
    });
    fCreate.on('submit', function(s){
        s.preventDefault();
        var f = $(this);
        $.ajax({
            url: f.attr('action'),
            data: f.serialize(),
            method: 'post',
            success: function(ss){
                sAlert('کاربر با موفقیت ایجاد شد', 2, function(){
                    document.location="/user/nav/?uid=" + ss;
                });
            },
            error: function(er){
                post_error(er);
            }
        });
    });
});