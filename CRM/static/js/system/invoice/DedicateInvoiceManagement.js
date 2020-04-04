$(function () {
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
        $('#fSdx').val(srh.serialize());
        reloadCurrent();
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
            mad.find('[data-dyna-del=1]').off('click').on('click', function(){
                var _this = $(this);
                _this.parent().remove();
                reCall();
            });
            bindMaxLen(mad);
            //bindSelect2(mad);
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
                reselectCurrent();
                sAlert('عملیات با موفقیت انجام شد', 2);
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
                reselectCurrent();
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
                reselectCurrent();
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
                reselectCurrent();
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
                    reloadCurrent();
                    mad.find('[type=submit]');
                    mad.modal('hide');
                },
                error: function(er){
                    post_error(er.responseText);
                    mad.find('[type=submit]');
                }
            })
        });
    });
    initGrid({
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
            }
        },
        ajax: true,
        url_prefix: '/factor/dedicate/',
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e, e2, r, summery) {
        $('#si').val(r[0].system_invoice_number);
        var row_description = $('<div>').addClass('row');
        var panel_description = $('<div>').addClass('panel panel-info').append($('<div>').addClass('panel-heading').append('<h4>').html('توضیحات'));
        var b_panel_description = $('<div>').addClass('panel-body').html(r[0].description);
        panel_description.append(b_panel_description);
        row_description.append(panel_description);
        summery.append(row_description);
        var t3 = $('<table>').addClass('table table-bordered').append($('<thead>').append($('<tr>').append(
            $('<th>').html('شناسه'),$('<th>').html('سرویس'),$('<th>').html('مدت زمان'),$('<th>').html('هزینه')
        )), $('<tbody>'));
        var tb3 = t3.find('tbody');
        var service_panel_b = $('<div>').addClass('panel-body').append(t3);
        var service_panel = $('<div>').addClass('panel panel-info').append($('<div>').addClass('panel-heading').html('سرویس ها'),service_panel_b);
        var service_row = $('<div>').addClass('row').append(service_panel);
        var t2 = $('<table>').addClass('table table-bordered').append($('<thead>').append($('<tr>').append(
            $('<td>').html('شناسه'),$('<td>').html('وضعیت'),$('<td>').html('زمان'),$('<td>').html('توضیحات'),$('<td>').html('کاربر')
        )), $('<tbody>'));
        var tb2 = t2.find('tbody');
        var state_history_row = $('<div>').addClass('row');
        var state_history_panel_b = $('<div>').addClass('panel-body').append(t2);
        var state_history_panel = $('<div>').addClass('panel panel-info').append($('<div>').addClass('panel-heading').html('گزارش وضعیت'), state_history_panel_b);
        state_history_row.append(state_history_panel);
        var t = $('<table>').addClass('table table-bordered').append($('<thead>').append('<tr>').append(
            $('<th>').html('شناسه'),$('<th>').html('نوع ارسال'),$('<th>').html('تاریخ ارسال'),$('<th>').html('تحویل گیرنده'),$('<th>').html('ارسال کننده')
        ), $('<tbody>'));
        var tb = t.find('tbody');
        var send_state_panel_b = $('<div>').addClass('panel-body').append(t);
        var send_state_panel = $('<div>').addClass('panel panel-info').append($('<div>').addClass('panel-heading').html('گزارش ارسال'), send_state_panel_b);
        var send_state_row = $('<div>').addClass('row').append(send_state_panel);

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
            },
            error: function(er){
                post_error(er);
            }
        });
        summery.append(service_row);
        summery.append(state_history_row);
        summery.append(send_state_row);
        summery.append(getActionArea());
        $.ajax({
            url: '/factor/dedicate/j/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                if(d.can_checkout){
                    if(d.system_invoice > 0){
                        summery.find('#bCheckout').addClass('hidden');
                        summery.find('#aInvoice').removeClass('hidden');
                    }
                    else{
                        summery.find('#bCheckout').removeClass('hidden');
                        summery.find('#aInvoice').addClass('hidden');
                    }
                }
                else{
                    summery.find('#bCheckout').addClass('hidden');
                    summery.find('#aInvoice').addClass('hidden');
                }
                if(d.has_file){
                    summery.find('#bUploaded').removeClass('hidden');
                }
                else{
                    summery.find('#bUploaded').addClass('hidden');
                }
                if(d.can_update_state){
                    summery.find('#bUpdateState').removeClass('hidden');
                }
                else{
                    summery.find('#bUpdateState').addClass('hidden');
                }
                if(d.can_send){
                    summery.find('#bUpdateSend').removeClass('hidden');
                }
                else{
                    summery.find('#bUpdateSend').addClass('hidden');
                }
                if(d.has_orphaned){
                    summery.find('#bSetReceiver').removeClass('hidden');
                }
                else{
                    summery.find('#bSetReceiver').addClass('hidden');
                }
            },
            error: function(er){
                post_error(er);
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
            },
            error: function(er){
                post_error(er);
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
            },
            error: function(er){
            }
        });
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
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