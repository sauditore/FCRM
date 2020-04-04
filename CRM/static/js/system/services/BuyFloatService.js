/**
    * Created by amirp on 1/30/2016
*/

$(function () {
    document.location = '#dfData';
    var frm = $('#fService');
    var sliders = {};
    var wiz = $('#wizard').steps({
        enablePagination: false,
        enableFinishButton: false,
        stepsOrientation: 'vertical',
        //transitionEffect: "slideLeft",
        titleTemplate: '#title#',
        tabs: true,
        labels: {
            cancel: "انصراف",
            current: "مرحله فعلی:",
            pagination: "صفحه بندی",
            finish: "پایان",
            next: "بعدی",
            previous: "قبلی",
            loading: "درحال بارگزاری...."
        },
        onStepChanging: function(v){
            return true;
        }
    });
    $('#bTM').on('click', function(be){
        sAlert('لطفا نام پیشنویس را وارد کنید', 4, function(data){
            if(data==false){
                return false;
            }
            if(data==''){
                swal.showInputError("انتخاب نام ضروری است");
                return false;
            }
            $.ajax({
                url: '/service/float/template/add/',
                method: 'post',
                data: frm.serialize()+'&t_name='+data,
                success: function(){
                    document.location = document.referrer;
                },
                error: function(er){
                    post_error(er, null, null);
                }
            });
        });

    });
    function selectService(v){
        var x = $('#serviceHolder').find('[data-pk='+parseInt(v)+']').removeClass('btn-primary').addClass('btn-success');
        $('[data-holder=1]').not(x).removeClass('btn-primary').addClass('btn-info');
        var sx = $('#sServices');
        sx.find('option').prop('selected', false);
        sx.find('[data-index='+parseInt(v)+']').prop('selected', true);
        $('#dViewService').html(sx.find(':selected').data('speed'));
        $.ajax({
            url: '/service/float/buy/options/?pk=' + sx.val(),
            method: 'get',
            dataType: 'json',
            success: function (d) {
                $('[data-option=1]').each(function (a, b) {
                    var bt = $(b);
                    if ($.inArray(parseInt(bt.attr('name')), d) < 0) {
                        bt.parent().addClass('hidden').prop('disabled', true);
                        bt.removeAttr('checked');
                    }
                    else {
                        bt.parent().removeClass('hidden').prop('disabled', false);
                    }
                });
                frm.submit();
            },
            error: function (er) {
                post_error(er, null, frm);
            }
        });
        frm.submit();
    }
    $('[data-wiz-page="1"]').on('click', function(be){
        be.preventDefault();
        $('#wizard').steps('next');
    });
    $('[data-wiz-page="2"]').on('click', function(be){
        be.preventDefault();
        $('#wizard').steps('previous');
    });
    $('#iXX').knob({
        "min":0,
        "max":$('#sServices').find('option').length,
        change: function(v){
            selectService(v);
        },
        release: function(v){
            selectService(v);
        }
    });
    $('#sServices').find('option').each(function (a, b) {
        $('#serviceHolder').append($('<div>').addClass('col-md-3 col-sm-4 col-xs-4').append($('<a>').addClass('btn btn-sm btn-info').append(
            $('<span>').addClass('hidden-sm hidden-xs').append($(b).text()), $('<span>').addClass('hidden-md hidden-lg').append($(b).text().substr(0, 4))
        ).attr({'data-pk': parseInt(a)+1, 'data-holder': '1', 'href': '#'+a}).on('click', function(ae){
            $(this).removeClass('btn-info').addClass('btn-primary');
            $('#iXX').val($(this).data('pk')).trigger('change');
        })))
    });
    $('[data-toggle="customValue"]').each(function (a, b) {
        var _that = $(this);
        _that.ionRangeSlider({
            min: _that.data('min'),
            max: _that.data('max'),
            from: _that.data('from'),
            onChange: function (a) {
                $('input[name=' + a.input.data('pk') + ']').val(parseInt(a.from));
                frm.submit();
            }
        });
        sliders[_that.data('pk')] = _that.data('ionRangeSlider');
    });
    $('[data-extra=1]').on('change', function () {
        sliders[$(this).attr('name')].update({from: $(this).val()});
        frm.submit();
    });
    var buy = $('#bBuy');
    $('#bAdd').on('click', function () {
        $('[name="t_name"]').val($('#t_name').val());
        $.ajax({
            url: '/service/float/template/add/',
            method: 'post',
            data: frm.serialize(),
            success: function () {
                $('#t_name').val('');
                $('[name="t_name"]').val('');
                load_templates();
            },
            error: function (er) {
                post_error(er, null, frm);
            }
        });
    });
    buy.on('click', function () {
        $.ajax({
            url: '/service/float/buy/invoice/',
            data: frm.serialize(),
            method: 'post',
            success: function (d) {
                document.location = $('#rx').val() + '?f=' + d+'&pk='+d; // Payment Bug Fix
            },
            error: function (er) {
                post_error(er, null, frm);
            }
        })
    });

    $('[data-extra-slider="1"]').on('change', function () {
        var _this = $(this);
        _this.prev().slider('setValue', parseInt(_this.val()));
    });
    $('[data-option=1]').on('change', function () {
        var b = $(this);
        $.ajax({
            url: '/service/float/buy/related/?pk=' + b.data('pk'),
            async: false,
            dataType: 'json',
            success: function (d) {
                if (d.length > 0) {
                    $('[data-xid]').each(function () {
                        var zx = $(this);
                        var cvb = zx.parent();
                        if ($.inArray(parseInt(zx.data('xid')), d) > -1) {
                            zx.addClass('hidden').data('locked', b.data('lock')).find('[name]').prop('disabled', true);
                            $('[data-pid=' + zx.data('xid') + ']').removeClass('hidden');
                            $('[href="#wizard-h-'+cvb.attr('id').split('-')[2]+'"]').addClass('hidden');
                        }
                        else {
                            zx.removeClass('hidden');
                            $('[data-pid=' + zx.data('xid') + ']').addClass('hidden');
                            $('[href="#wizard-h-'+cvb.attr('id').split('-')[2]+'"]').removeClass('hidden');
                        }
                    });
                }
                else {
                    $('[data-xid]').each(function () {
                        var zx = $(this);
                        if (zx.data('locked') == b.data('lock')) {
                            var cvb = zx.parent();
                            zx.removeClass('hidden').find('[name]').prop('disabled', false);
                            $('[data-pid=' + zx.data('xid') + ']').addClass('hidden');
                            $('[href="#wizard-h-'+cvb.attr('id').split('-')[2]+'"]').removeClass('hidden');
                        }
                    });
                }
                if (b.is(':checked')) {
                    b.parent().parent().parent().find('[type="checkbox"]').not(b).not('.hidden').prop('checked', false);
                }
                frm.submit();
                $('#wizard').steps('next');
            },
            error: function (er) {
                post_error(er, null, frm);
            }
        });
    });
    frm.off('submit').on('submit', function (fs) {
        fs.preventDefault();
        $.ajax({
            url: '/service/float/buy/cal/?',
            data: frm.serialize(),
            method: 'get',
            dataType: 'json',
            success: function (d) {
                var tpx = $('[data-summery="1"]');
                var t_less = $('[data-less-summery=1]').find('tbody');
                t_less.empty();
                var tp = tpx.find('tbody');
                tp.empty();
                $.each(d.data, function (a, b) {
                    var tr = $('<tr>');
                    var td0 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    td0.html(b.name);
                    if(b.price == 0){
                        td1.append($('<span>').addClass('text-info').append($('<i>').addClass('fa fa-check')));
                        td2.append($('<span>').addClass('text-info').append($('<i>').addClass('fa fa-check')));
                    }
                    else if(b.price== -1){
                        td1.append($('<span>').addClass('text-danger').append($('<i>').addClass('fa fa-remove')));
                        td2.append($('<span>').addClass('text-danger').append($('<i>').addClass('fa fa-remove')));
                    }
                    else{

                        td1.append(get_price_cell_formatter(b.price, false, false));
                        td2.append(get_price_cell_formatter(b.op_price, false, false));
                    }
                    tr.append(td0 , td1, $('<td>').html((b.value || '-') + ' '+ (b.metric || '-')), td2);
                    t_less.append(tr.clone());
                    tp.append(tr.clone());
                });
                var debit = $('<span>').append(get_price_cell_formatter(d.debit, false, true));
                tp.append($('<tr>').append($('<td>').html('مدت سرویس'), $('<td>').html(d.period + ' ماه')));
                if(d.discount)
                    tp.append($('<tr>').append($('<td>').html('تخفیف'), $('<td>').html(d.discount + ' روز')));
                if(d.extra_package){
                    tp.append($('<tr>').append($('<td>').html('حجم هدیه'), $('<td>').html(d.extra_package + ' مگابایت')));
                }
                //tp.append($('<tr>').append($('<td>').html('هزینه ۱ ماه'), $('<td>').append($('<span>').addClass('price').append(d.one_month_price))));
                tp.append($('<tr>').append($('<td>').html('پس انداز'), $('<td>').append(debit)));
                tp.append($('<tr>').append($('<td>').html('هزینه کل سرویس'), $('<td>').append(get_price_cell_formatter(d.total, false, false))));
                tp.append($('<tr>').append($('<td>').html('مالیات'), $('<td>').append(get_price_cell_formatter(d.tax, false, false))));
                tp.append($('<tr>').append($('<td>').html('مبلغ قابل پرداخت'), $('<td>').append(get_price_cell_formatter(d.price_with_debit, false, false))));
                formatPrice($('#wizard'));
            },
            error: function (er) {
                post_error(er, null, frm);
            }
        })
    });
    $('#iXX').val($('#sServices').find('option:selected').data('index')).trigger('change');
    if($('#hRCH').length>0){
        //setTimeout(function(){
            $('[data-required]').trigger('change');
        //}, 5000);
        //frm.submit();
    }
});
