/**
 * Created by saeed on 1/5/2016.
 */

$(function(){
    $('[data-buy=1]').on('click', function(be){
        var b = $(this);
        b.addClass('m-progress');
        $.ajax({
            url: '/factor/debit/package/invoice/?pk='+ b.data('pk'),
            method: 'get',
            success: function(){
                document.location = '/factor/show/all/'
            },
            error: function(er){
                alert(er.responseText);
            }
        });
    });
});