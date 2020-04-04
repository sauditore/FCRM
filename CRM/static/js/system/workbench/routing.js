/**
    * Created by saeed on 5/21/16
    */

$(function(){
    var f = $('.ibox-content').find('form');
    $('[type=checkbox]').on('change', function(){
        var $this = $(this);
        var p = $this.parents().find('.panel').has($this);
        if($this.is(':checked')){
            p.addClass('panel-primary').removeClass('panel-warning');
        }
        else {
            p.removeClass('panel-primary').addClass('panel-warning');
        }
    });
    f.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '',
            method: 'post',
            data: $(this).serialize(),
            success: function(){
                sAlert('وضعیت رویداد با موفقیت تغییر یافت', 2);
            },
            error: function(er){
                post_error(er, null, $(this));
            }
        });
    })
});
