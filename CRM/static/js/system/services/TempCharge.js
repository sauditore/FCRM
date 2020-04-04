/**
 * Created by saeed on 3/16/16.
 */
$(function(){
    function calculate_price(){
        var pp = parseInt($('#hpp').val() || 0);
        var dp = parseInt($('#hdp').val() || 0);
        var sp = parseInt($('[name=c]').val() || 0);
        var sd = parseInt($('[name=d]').val() || 0);
        if(isNaN(pp)){
            pp =0;
        }
        if(isNaN(dp)){
            dp = 0;
        }
        if(isNaN(sp)){
            sp = 0;
        }
        if(isNaN(dp)){
            sd = 0;
        }
        var tp = (sp*(pp/1024)) + (sd*dp);
        $('#sPrice').html(parseInt(tp) + ' تومان');

    }
    var sl = $('#sPack');
    var dl = $('#sDays');
    sl.css('color', '#18a689').html('0');
    dl.css('color', '#18a689').html('0');
    var sliders = $('[data-slider-id]');
    sliders.each(function(a,b){
        var _that = $(this);
        _that.ionRangeSlider({
        min: _that.data('min'),
        max: _that.data('max'),
        from: _that.data('from'),
        onChange: function (a) {
            $('input[name=' + a.input.data('pk') + ']').val(parseInt(a.from));
            $('#'+a.input.data('lbl')).html(a.from);
            calculate_price();
        }});
    });

    sliders.on('slide', function(){
        var _this = $(this);
        _this.next().val(_this.slider('getValue'));
    });
    $('[data-extra-slider="1"]').on('change', function(){
        var _this = $(this);
        _this.prev().data('ionRangeSlider').update({from:parseInt(_this.val())});
        calculate_price();
    });
    $('#fTemp').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/temp/?',
            method: 'get',
            data: $(this).serialize(),
            success: function(dx){
                console.log(dx);
                if(dx == '200'){
                    sAlert('شارژ موقت با موفقیت انجام شد', 2);
                    document.location = '/user/nav/?uid='+$('[name=u]').val();
                }
                else{

                    {
                        document.location = dx;
                    }
                    // else{
                    //     sAlert('عملیات با خطا مواجه شده است', 2);
                    // }
                }
                
            },
            error: function(er){
                post_error(er);
            }
        });
    });
});