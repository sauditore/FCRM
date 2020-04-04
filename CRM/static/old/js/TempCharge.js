/**
 * Created by saeed on 3/16/16.
 */
$(function(){
    var sliders = $('[data-slider-id]');
    sliders.slider({
        tooltip: 'always'
    });
    sliders.on('slide', function(){
        var _this = $(this);
        _this.next().val(_this.slider('getValue'));
    });
    $('[data-extra-slider="1"]').on('change', function(){
        var _this = $(this);
        _this.prev().slider('setValue', parseInt(_this.val()));
    });
    $('#fTemp').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/temp/?',
            method: 'get',
            data: $(this).serialize(),
            success: function(){
                alert(123);
            },
            error: function(er){
                post_error(er.responseJSON.msg);
            }
        });
    });
});