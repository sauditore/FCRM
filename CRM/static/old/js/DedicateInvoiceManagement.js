$(function () {
    var tdi = $('#tDedicatedInvoice');
    var mad = $('#mAddNewInvoice');
    var fad = $('#fAddNewInvoice');
    var ain = $('#aInvoice');
    var mpa = $('#mPay');
    var fpa = $('#fPay');
    var fcs = $('#fChangeState');
    var mcs = $('#mChangeState');
    var mus = $('#mUpdateSendType');
    var fus = $('#fUpdateSendType');
    var mss = $('#mSetRSV');
    var fss = $('#fSetRSV');
    var bAdd = $('#bAddNew');
    var srh = $('#search');
    var mdl = $('#mDownload');
    mdl.on('show.bs.modal', function(me){
        mdl.find('[name=pk]').val($(me.relatedTarget).data('pk'));
        mdl.off('submit').on('submit', function(){
            mdl.modal('hide');
        });
    });
    srh.on('submit', function(fs){
        fs.preventDefault();
        reload_grid(tdi);
    });
    bAdd.on('click', function(){
        function reCall(_this){
            var sm = $('#lSum');
            var t_outer = 0;
            if(_this != undefined){
                var c = parseInt(_this.val());
                if (isNaN(c)){
                    _this.val('');
                    return;
                }
            }
            holder.find('.form-inline').each(function(j,k){
                var _k = $(k);
                var t_inner = 1;
                _k.find('input').each(function(n,m){
                    var t0 = parseInt($(m).val());
                    if(!isNaN(t0)){
                        t_inner *= t0;
                    }
                    else{
                        t_inner = 0;
                    }
                });
                t_outer += t_inner;
            });
            var dc = parseInt($('[name=dp]').val());
            if(isNaN(dc)){
                dc = 0;
            }
            t_outer -= dc;
            sm.val(t_outer);
        }
        function reloadEvents(){
            mad.find('[data-float=1]').floatlabel({
                labelClass: 'form-group-float-persian'
            });
            mad.find('[data-dyna-del=1]').off('click').on('click', function(){
                var _this = $(this);
                _this.parent().remove();
                reCall();
            });
        }
        var holder = $('#dH');
        var nm = holder.find('.form-inline').find('input').size();
        var other = holder.find('.form-inline').first().clone();
        other.find('input,select').each(function(y,z){
            var x2 = $(z);

            x2.attr('name', x2.attr('name').replace('0', nm));
        });
        other.removeClass('hidden').find('button').removeClass('hidden');
        other.find('input').on('change', function(te){
            var _this = $(this);
            reCall(_this);
        });
        $('[name=dp]').off('change').on('change', function(e){
            reCall($(this));
        });
        holder.append(other);
        reloadEvents();
    });
    mss.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mss.find('[name=pk]').val(btn.data('pk'));
    });
    fss.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/factor/dedicate/srv/?',
            method: 'get',
            data: fss.serialize(),
            success: function(){
                mss.modal('hide');
                reselect_grid(tdi);
                post_ok('ر حال بارگزاری مجدد');
            },
            error: function(er){
                post_error(er.responseText);
            }
        });
    });
    mus.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mus.find('[name=pk]').val(btn.data('pk'));
    });
    fus.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/factor/dedicate/uss/?',
            method: 'get',
            data: fus.serialize(),
            success: function(){
                mus.modal('hide');
                reselect_grid(tdi);
            },
            error: function(er){
                post_error(er.responseText);
            }
        });
    });
    mcs.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mcs.find('[name=pk]').val(btn.data('pk'));
    });
    fcs.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/factor/dedicate/ups/',
            data: fcs.serialize(),
            method: 'post',
            success: function(){
                mcs.modal('hide');
                reload_grid(tdi);
            },
            error: function(er){
                post_error(er.responseText);
            }
        });
    });
    ain.on('click', function(){
        ain.attr('href', '/factor/show/all/?pk=' + $('#si').val());
    });
    mpa.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mpa.find('input').val('');
        mpa.find('textarea').html('');
        mpa.find('[name="pk"]').val(btn.data('pk'));
    });
    fpa.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/factor/dedicate/checkout/?',
            method: 'get',
            data: fpa.serialize(),
            success: function(){
                reselect_grid(tdi);
                mpa.modal('hide');
            },
            error: function(er){
                post_error(er.responseText);
            }
        })
    });
    $('[data-date=1]').persianDatepicker();
    mad.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        mad.find('[name=u]').val(btn.data('uid'));
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/factor/dedicate/j/?pk='+btn.data('pk'),
                method: 'get',
                success: function(d){

                },
                error: function(er){
                    post_error(er.responseText);
                }
            });
        }
        fad.off('submit').on('submit', function(fs){
            fs.preventDefault();
            mad.find('[type=submit]').addClass('m-progress');
            $.ajax({
                url: '/factor/dedicate/add/',
                data: fad.serialize(),
                method: 'post',
                success: function(){
                    tdi.bootgrid('reload');
                    mad.find('[type=submit]').removeClass('m-progress');
                    mad.modal('hide');
                },
                error: function(er){
                    post_error(er.responseText);
                    mad.find('[type=submit]').removeClass('m-progress');
                }
            })
        });
    });
    tdi.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'invoice_number': function(c, r){
                if(r.invoice_number){
                    return r.invoice_number;
                }
                return r.system_invoice_number;
            },
            'pre_invoice': function(c, r){
                if(r.is_pre_invoice){
                    return $('<span>').append($('<i>').addClass('glyphicon glyphicon-check').clone()).html();
                }
                else{
                    return $('<span>').append($('<i>').addClass('glyphicon glyphicon-remove').clone()).html();
                }
            },
            'i_state': function(c, r){
                var a = r.fk_dedicated_invoice_state_invoice__state;
                return tr_state(a, r.fk_dedicated_invoice_state_invoice__next_change);
                //var res = $('<span>');
                //var i = $('<i>');
                //i.addClass('glyphicon');
                //var t = '';
                //if(a==0){
                //    t = 'نامعلوم';
                //    i.addClass('glyphicon-question-sign text-danger');
                //}
                //else if(a == 1){
                //    t = 'آماده سازی';
                //    i.addClass('glyphicon-print');
                //}
                //else if(a == 2){
                //    t = 'در حال ارسال';
                //    i.addClass('glyphicon-envelope');
                //}
                //else if(a == 3){
                //    t = 'ارسال شد';
                //    i.addClass('glyphicon-plane');
                //}
                //else if(a == 4){
                //    t = 'پیگیری بعدی';
                //    i.addClass('glyphicon-time text-info');
                //}
                //else if(a == 5){
                //    t = 'پیگیری در تاریخ'+' ' + r.fk_dedicated_invoice_state_invoice__next_change;
                //    i.addClass('glyphicon-calendar text-warning');
                //}
                //else if(a == 6){
                //    t = 'تحویل داده شده';
                //    i.addClass('glyphicon-user');
                //}
                //else if(a == 7){
                //    t = 'تسویه شده';
                //    i.addClass('glyphicon-check text-success');
                //}
                //else{
                //    t = 'نامعلوم';
                //    i.addClass('glyphicon-question-sign text-danger');
                //}
                //res.html(t);
                //return $('<div>').append(i, $('<span>').html(' '),res).clone().html();
            }
        },
        ajax: true,
        url: function () {
            return '/factor/dedicate/?'+srh.serialize();
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function (e, r) {
        $('[data-need-pk=1]').data('pk', r[0].ext).not('[data-manual="1"]').removeClass('hidden');
        $('#si').val(r[0].system_invoice_number);
        $.ajax({
            url: '/factor/dedicate/j/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                if(d.can_checkout){
                    if(d.system_invoice > 0){
                        $('#bCheckout').addClass('hidden');
                        $('#aInvoice').removeClass('hidden');
                    }
                    else{
                        $('#bCheckout').removeClass('hidden');
                        $('#aInvoice').addClass('hidden');
                    }
                }
                else{
                    $('#bCheckout').addClass('hidden');
                    $('#aInvoice').addClass('hidden');
                }
                if(d.has_file){
                    $('#bUploaded').removeClass('hidden');
                }
                else{
                    $('#bUploaded').addClass('hidden');
                }
                if(d.can_update_state){
                    $('#bUpdateState').removeClass('hidden');
                }
                else{
                    $('#bUpdateState').addClass('hidden');
                }
                if(d.can_send){
                    $('#bUpdateSend').removeClass('hidden');
                }
                else{
                    $('#bUpdateSend').addClass('hidden');
                }
                if(d.has_orphaned){
                    $('#bSetReceiver').removeClass('hidden');
                }
                else{
                    $('#bSetReceiver').addClass('hidden');
                }
            },
            error: function(er){
                post_error(er.responseText);
            }
        });
        $('#dDescription').removeClass('hidden').find('div').html(r[0].description);
        var t2 = $('#tStateHistory');
        var t = $('#tSendHistory');
        var t3 = $('#tSrv');
        var tb = t.find('tbody');
        var tb2 = t2.find('tbody');
        var tb3 = t3.find('tbody');
        light_loading(t2);
        light_loading(t);
        light_loading(t3);
        tb.empty();
        tb2.empty();
        tb3.empty();
        $.ajax({
            url: '/factor/dedicate/srx/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d, function(a,b){
                    var tr = $('<tr>');
                    tr.append($('<td>').html(b.pk), $('<td>').html(b.service__name), $('<td>').html(b.period), $('<td>').html(b.price));
                    tb3.append(tr);
                });
                light_loaded(t3);
            },
            error: function(er){
                post_error(er.responseText);
                light_loaded(t3);
            }
        });
        $.ajax({
            url: '/factor/dedicate/chi/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d.rows, function(a,b){
                    var tr = $('<tr>');
                    tr.append($('<td>').html(b.pk), $('<td>').html(tr_state(b.state)), $('<td>').html(b.update_time), $('<td>').html(b.extra_data), $('<td>').html(b.user__first_name));
                    tb2.append(tr);
                });
                light_loaded(t2);
            },
            error: function(er){
                post_error(er.responseText);
                light_loaded(t2);
            }
        });
        $.ajax({
            url: '/factor/dedicate/shi/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d.rows, function(a,b){
                    var tr = $('<tr>');
                    tr.append($('<td>').html(b.pk), $('<td>').html(b.send_type__name), $('<td>').html(b.change_date), $('<td>').html(b.receiver), $('<td>').html(b.user__first_name));
                    tb.append(tr);
                });
                light_loaded(t);
            },
            error: function(er){
                post_error(er.responseText);
                light_loaded(t);
            }
        });
    });
});
function tr_state(r, ex){
    var a = r;
    var res = $('<span>');
    var i = $('<i>');
    i.addClass('glyphicon');
    var t = '';
    if(a==0){
        t = 'نامعلوم';
        i.addClass('glyphicon-question-sign text-danger');
    }
    else if(a == 1){
        t = 'آماده سازی';
        i.addClass('glyphicon-print');
    }
    else if(a == 2){
        t = 'در حال ارسال';
        i.addClass('glyphicon-envelope');
    }
    else if(a == 3){
        t = 'ارسال شد';
        i.addClass('glyphicon-plane');
    }
    else if(a == 4){
        t = 'پیگیری بعدی';
        i.addClass('glyphicon-time text-info');
    }
    else if(a == 5){
        if(ex!=undefined){
            t = 'پیگیری در تاریخ'+' ' + ex;
        }
        else{
            t = 'پیگیری مجدد';
        }
        i.addClass('glyphicon-calendar text-warning');
    }
    else if(a == 6){
        t = 'تحویل داده شده';
        i.addClass('glyphicon-user');
    }
    else if(a == 7){
        t = 'تسویه شده';
        i.addClass('glyphicon-check text-success');
    }
    else{
        t = 'نامعلوم';
        i.addClass('glyphicon-question-sign text-danger');
    }
    res.html(t);
    return $('<div>').append(i, $('<span>').html(' '),res).clone().html();
}