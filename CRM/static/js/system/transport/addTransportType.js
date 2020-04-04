/**
 * Created by saeed on 12/5/2015.
 */

$(function(){
    var fm = $('#fAddTransportType');
    var m = $('#mAddTransportType');
    m.on('show.bs.modal', function(){
        fm.off('submit').on('submit', function(fs){
            fs.preventDefault();
            fm.find('[type=submit]').button('loading');
            $.ajax({
                url: '/transport/types/add/',
                method: 'post',
                data: $(this).serialize(),
                success: function(){
                    m.modal('hide');
                    fm.find('[type=submit]').button('reset');
                },
                error: function(er){
                    m.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        m.find('.alert').addClass('hidden');
                    }, 5000);
                    fm.find('[type=submit]').button('reset');
                }
            });
        });
        m.find('.alert').addClass('hidden');
        fm.find('[type=submit]').button('reset');
    });
});