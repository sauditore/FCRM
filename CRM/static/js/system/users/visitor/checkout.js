/**
    * Created by saeed on 5/21/16.
    */

$(function(){
    var m = $('#mVisitorCheckout');
    var f = m.find('form');
    m.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        m.find('[name=u]').val(btn.data('pk'));
    });
    f.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: f.attr('action'),
            method: 'get',
            data: f.serialize(),
            success: function(){
                sAlert('تغییرات با موفقیت انجام شد', 2);
                location.reload();
            },
            error: function (er) {
                post_error(er, null, m);
            }
        })
    });
});
