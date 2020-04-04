/**
 * Created by saeed on 4/10/16.
 */

$(function(){
    $('#mAdminPayment').on('show.bs.modal', function(em){
        var m = $(em.target);
        clear_on_open(m);
        var b = $(em.relatedTarget);
        var f = $('#fPayByAdmin');
        m.find('.alert').addClass('hidden');
        f.find('input[name=f]').val(b.data('pk'));
        f.off('submit');
        f.on('submit', function(fe){
            fe.preventDefault();
            $.ajax({
                url: f.attr('action')+"?" + f.serialize(),
                method: 'get',
                success: function(){
                    reloadCurrent();
                    m.modal('hide');
                    sAlert('پرداخت با موفقیت انجام شد',2);
                },
                error: function(er){
                    post_error(er, null, m);
                }
            });
        });
    });
});
