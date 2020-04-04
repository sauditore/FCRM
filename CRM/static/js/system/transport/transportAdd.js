/**
 * Created by saeed on 12/6/2015.
 */

$(function(){
    var mt = $('#mAddNewTransport');
    var ft = $('#fAddNewTransport');
    mt.off().on('show.bs.modal', function(){
        mt.find('.alert').addClass('hidden');
        mt.find('input').val('');
        $.ajax({
            url: '/transport/types/',
            method: 'get',
            dataType: 'json',
            success: function(d){
                var stt = $('#sTTypes');
                stt.empty();
                $.each(d.data, function(a,b){
                    var o = $('<option>');
                    o.val(b.external).html(b.name);
                    stt.append(o);
                });
            },
            error: function(er){
                mt.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                setTimeout(function(){
                    mt.find('.alert').addClass('hidden');
                }, 5000);
            }
        });
    });
    ft.off().on('submit', function(fts){
        fts.preventDefault();
        ft.find('[type=submit]').button('loading');
        $.ajax({
            url: '/transport/add/',
            method: 'post',
            data: ft.serialize(),
            success: function(){
                mt.modal('hide');
                ft.find('[type=submit]').button('reset');
                $('#tTrans').bootgrid('reload');
            },
            error: function(er){
                mt.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                setTimeout(function(){
                    mt.find('.alert').addClass('hidden');
                }, 5000);
                ft.find('[type=submit]').button('reset');
            }
        });
    });
});