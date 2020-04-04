$(function () {
    function get_float_service_details(iv, sm){
        $.ajax({
            url: '/factor/float/items/?pk='+iv,
            method: 'get',
            dataType: 'json',
            success: function(d){
                var t = $('#tFloats').clone().removeClass('hidden').find('tbody').empty();
                sm.prepend(t.parent());
                $.each(d.options, function(a, b){
                    var tr = $('<tr>');
                    tr.append(
                        $('<td>').html(b.option__group__name),
                        $('<td>').html(b.option__name),
                        $('<td>').append(b.value==0?$('<i>').addClass('fa fa-check text-success'): b.value),
                        $('<td>').append(b.total_price==0?$('<i>').addClass('fa fa-check text-success'): $('<span>').append($('<span>').addClass('price').html(b.total_price)).append(' تومان'))
                    );
                    t.append(tr);
                    formatPrice(tr);
                });
            },
            error: function(er){
                post_error(er, null, null);
            }
        })
    }
    function get_temp_charge_details(iv, sm){
        $.ajax({
            url: '/factor/temp/items/?pk='+iv,
            method: 'get',
            dataType: 'json',
            success: function(d){
                var t = $('<table>').addClass('table table-info');
                var tr0 = $('<tr>');
                tr0.append(
                    $('<td>').html('مقدار اعتبار'),
                    $('<td>').html('هزینه اعتبار'),
                    $('<td>').html('مدت شارژ'),
                    $('<td>').html('هزینه شارژ')
                );
                t.append(
                    $('<thead>').append(tr0),
                    $('<tbody>').append(
                        $('<tr>').append(
                            $('<td>').html(d.credit + ' مگابایت'),
                            $('<td>').append(get_price_cell_formatter(d.credit_price, false, false)),
                            $('<td>').html(d.days + ' روز'),
                            $('<td>').append(get_price_cell_formatter(d.days_price, false, false))
                        )
                    )
                );
                sm.prepend(t);
            },
            error: function(er){
                post_error(er, null, null);
            }
        });
    }
    function get_price_cell(price, debit, dynamic_discount, add_total_payment){
        var d = $('<div>');
        var x = $('<span>').append($('<span>').addClass('price').html(get_price_cell_formatter(price, true)));
        var s = $('<span>').addClass('label price');
        var dd = $('<span>').addClass('label price');
        var tt = $('<span>').addClass('label price');
        if(debit < 0){
            s.addClass('label-danger');
            s.html(get_price_cell_formatter(debit, true));
        }
        else if(debit > 0){
            s.addClass('label-success');
            s.html(get_price_cell_formatter(debit, true));
        }
        if(dynamic_discount!=undefined) {
            if (dynamic_discount != 0) {
                dd.html(get_price_cell_formatter(dynamic_discount, true)).addClass('label-default');
            }
        }
        d.append($('<div>').addClass('text-center').append(x),
            $('<div>').addClass('text-center').append(dd),
            $('<div>').addClass('text-center').append(s));
        if(add_total_payment===true){
            var tx = 0;
            if(debit){
                tx = price-debit;
            }
            else{
                tx = price
            }
            if(dynamic_discount){
                tx = tx + dynamic_discount
            }
            tt.addClass('label-info').html(get_price_cell_formatter(tx, true));
            d.append(
                $('<div>').addClass('text-center').append(tt)
            )
        }
        return d.html();
    }
    $('[data-date=1]').datepicker({ isRTL: true , dateFormat: 'yy/m/d'});
    $('#fSearch').on('submit', function(fs){
        fs.preventDefault();
        $('#fSdx').val($(this).serialize());
        reloadCurrent();
        document.location = '#';
        document.location = '#tInvoices';
    });
    $('#sGroups').on('change', function() {
        var ucs = $('#userCurrentServices');
        var packs = $('#sPackages');
        var srv = $('#sServices');
        srv.empty().append($('<option>').html('-'));
        packs.empty().append($('<option>').html('-'));
        ucs.empty().append($('<option>').html('-'));
        $.ajax({
            url: "/factor/services/j/?g=" + $(this).val(),
            method: 'get',
            dataType: 'json',
            success: function (d) {
                $.each(d.services, function (a, b) {
                    var o = $('<option>');
                    o.val(b.pk);
                    o.html(b.name);
                    ucs.append(o);
                    srv.append(o.clone());
                });
                $.each(d.packages, function (y, z) {
                    var o = $('<option>');
                    o.val(z.pk);
                    o.html(z.name);
                    packs.append(o);
                });
            }
        });
    });
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    $('#bDEX').on('click', function(){
        document.location = '/factor/excel/?'+$('#fSdx').val();
    });
    mad.on('show.bs.modal', function (me) {
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if (btn.data('pk') != undefined) {
            $.ajax({
                method: 'get',
                url: '/webAddress/j/?pk=' + btn.data('pk'),
                dataType: 'json',
                success: function (d) {
                    mad.find('[name=pk]').val(d.pk);

                },
                error: function (er) {
                    show_error(er.responseText);
                }
            });
        }
    });
    fad.on('submit', function (fs) {
        fs.preventDefault();
        $.ajax({
            url: '/addAddress/add/',
            method: 'post',
            data: fad.serialize(),
            success: function () {
                mad.modal('hide');
                reloadCurrent();
                sAlert('تغییرات با موفقیت انجام شد', 2);
            },
            error: function (er) {
                post_error(er, null, mad);
            }
        })
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'linker': function(c,r){
                var n = '';
                if(c.id == 'user__fk_ibs_user_info_user__ibs_uid'){
                    n = r.user__fk_ibs_user_info_user__ibs_uid;
                }
                else{
                    n = r.user__first_name;
                }
                var x = $('<a>').attr('href', '/user/nav/?uid='+ r.user__pk).html(n);
                return $('<div>').append(x).clone().html();
            },
            'state': function(c,r){
                var i = $('<i>').addClass('fa');
                if(r.is_paid){
                    i.addClass('fa-check text-success');
                }
                else{
                    i.addClass('fa-remove text-danger');
                }
                return $('<div>').append(i).html();
            },
            'price': function(c,r){
                return get_price_cell(r.price, r.debit_price, r.dynamic_discount, true);
            }
        },
        ajax: true,
        url_prefix: "/factor/show/all/",
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
        var a = $('<div>').addClass('text-center').append(getActionArea());
        var tbl = $('<table>').addClass('table table-info');
        var t_head = $('<thead>');
        var t_body = $('<tbody>');
        var dsc = $('<div>').addClass('row').append($('<div>').addClass('col-md-12').append($('<p>').html(r[0].comment)));
        t_head.append($('<tr>').append($('<th>').addClass('text-center').html('سرویس فعلی'),
            $('<th>').addClass('text-center').html('تاریخ انقضا'),
            $('<th>').addClass('text-center').html('تخفیف')));
        t_body.append($('<tr>').append($('<td>').html(r[0].user__fk_user_current_service_user__service__name),
            $('<td>').html(r[0].expire_date),
            $('<td>').html('-')));
        summery.append(dsc,tbl.append(t_head, t_body),a);
        rebindModal(summery);
        summery.find('[data-need-pk]').data('pk', r[0].pk);
        summery.find('[name=f]').val(r[0].pk);
        summery.find('[data-need-cpk=1]').data('cpk', r[0].user__pk);
        bindDelete(summery);
        if(r[0].is_paid){
            summery.find('#fPayment').addClass('hidden');
            summery.find('[data-target="#mAdminPayment"]').addClass('hidden');
        }
        if(r[0].service__service_type==12){
            get_float_service_details(r[0].pk,summery);
        }
        else if(r[0].service__service_type==6){
            get_temp_charge_details(r[0].pk, summery);
        }
        summery.find('[data-action="pr"]').on('click', function(ae){
            ae.preventDefault();
            window.open($(this).attr('href')+'?pk='+$(this).data('pk'), '_blank');
        });
    }).on('loaded.grid', function(){
        //formatPrice($('body'));
    });
});
