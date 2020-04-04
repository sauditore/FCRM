$(function(){
    $('#cSP').on('change', function(){
        $('#f2').submit();
    });
    $('[type=text]').priceFormat({
        thousandsSeparator: ',',
        prefix: '',
        clearPrefix: true,
        centsLimit: 0
    });
    $('#f1').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: $(this).attr('action'),
            method: 'post',
            data: $(this).serialize(),
            dataType: 'json',
            success: function(d){
                $('#sSAtOnce').html(d.once);
                $('#sSMonthly').html(d.monthly);
                $('#sSInternet').html(d.internet);
                formatPrice($('body'));
            },
            error: function(er){
                post_error(er);
            }
        })
    });
    $('#f2').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            method: 'post',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            dataType: 'json',
            success: function(d){
                $('#sDOnce').html(d.once);
                $('#sDMonthly').html(d.monthly);
                $('#sDInternet').html(d.internet);
                //if(parseInt(d.once)==0){
                //    sAlert('مبلغ فروش حداقل باید بیشتر از 250 هزار تومان باشد', 5);
                //}
                formatPrice($('body'));
            },
            error: function(er){
                sAlert(er.responseJSON.msg, 5);
            }
        });
    });
    $('#f3').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            method: 'post',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            dataType: 'json',
            success: function(d){
                $('#sIOnce').html(d.once);
                $('#sIMonthly').html(d.monthly);
                //if(parseInt(d.once)==0){
                //    sAlert('مبلغ فروش حداقل باید بیشتر از 250 هزار تومان باشد', 5);
                //}
                formatPrice($('body'));
            },
            error: function(er){
                sAlert(er.responseJSON.msg, 5);
            }
        });
    });
});