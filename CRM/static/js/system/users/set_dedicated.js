/**
 * Created by saeed on 5/7/16.
 */

$(function(){
    var m = $('#mAddDedicated');
    var f = m.find('form');
    m.on('show.bs.modal', function(me){
        m.find('[name=pk]').val($(me.relatedTarget).data('pk'));
    });
    f.on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: f.attr('action'),
            method: 'get',
            data: f.serialize(),
            success: function(){
                m.modal('hide');
                sAlert('عملیات با موفقیت انجام شد', 2, function(){
                    location.reload();
                });
            },
            error: function(er){
                post_error(er);
            }
        })
    });
});
