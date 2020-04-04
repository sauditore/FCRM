/**
 * Created by saeed on 5/7/16.
 */

$(function(){
    var m = $('#mSetCo');
    var f = m.find('form');
    m.on('show.bs.modal', function(e){
        m.find('[name=pk]').val($(e.relatedTarget).data('pk'));
    });
    f.on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/user/set_co/',
            method: 'get',
            data: f.serialize(),
            success: function(){
                m.modal('hide');
                sAlert('اطلاعات شخص حقیقی با موفقیت ثبت شد', 2, function(){
                    location.reload();
                });
            },
            error: function(er){
                post_error(er);
            }
        })
    })
});
