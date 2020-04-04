$(function () {
    var ma = $('#mAddNewEquipmentType');
    var fa = $('#fAddNewEquipmentType');
    var fd = $('#fDelEquipmentType');
    var md = $('#mDelEquipmentType');
    var sub = $('#tSubGroup');
    var xmb = '';
    $('#fAddOrderForTypes').on('submit', function(fs){
        fs.preventDefault();
        var f = $(fs.target);
        $.ajax({
            url: '/equipment/order/add/',
            method: 'post',
            data: f.serialize(),
            success: function(){
                location.reload();
            },
            error: function(er){
                post_error(er, null);
            }
        });
    });
    $('[type=radio]').on('change', function(){
        var t = $(this);
        $('[data-need-toggle=1]').prop('disabled', 'disabled');
        if(t.is(':checked')){
            $(t.data('target')).prop('disabled', false);
        }
    });
    $('[name=u]').select2({
        placeholder: "کاربر",
        ajax: {
            url: '/user/au/',
            dataType: 'json',
            delay: 500,
            data: function (params) {
                return {
                    query: params.term, // search term
                    page: params.page
                    };
            },
            processResults: function(data){
                var res = [];
                $.each(data, function(a,b){
                    //noinspection JSUnresolvedVariable
                    res.push({text: b.first_name, id: b.id})
                });
                return {
                    results: res,
                    pagination: {}
                };
            }
        }
    });
    $('[name=t]').select2({
        placeholder: "برج",
        ajax: {
            url: '/tower/au/',
            dataType: 'json',
            delay: 500,
            data: function (params) {
                return {
                    query: params.term, // search term
                    page: params.page
                    };
            },
            processResults: function(data){
                var res = [];
                $.each(data, function(a,b){
                    res.push({text: b.name, id: b.id})
                });
                return {
                    results: res,
                    pagination: {}
                };
            }
        }
    });
    $('[name=ps]').select2({
        placeholder: "شبکه",
        ajax: {
            url: '/pops/au/',
            dataType: 'json',
            delay: 500,
            data: function (params) {
                return {
                    query: params.term, // search term
                    page: params.page
                    };
            },
            processResults: function(data){
                var res = [];
                $.each(data, function(a,b){
                    res.push({text: b.name, id: b.id})
                });
                return {
                    results: res,
                    pagination: {}
                };
            }
        }
    });

    sub.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'price': function(c,r){
                var p = '';
                if(c.id == 'code__sell_price'){
                    p = r.code__sell_price;
                }
                if(c.id == 'code__used_sell_price'){
                    p = r.code__used_sell_price;
                }
                return '<span data-price="1">'+ p + '</span>';
            }
        },
        ajax: true,
        url: function(){
            return '/equipment/type/sub/?pk='+xmb;
        },
        labels:{
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function(e, r){
        $('#dOrderContainer').removeClass('hidden');
        sub.bootgrid('deselect');
        var last_used_action;
        var last_used_pk;
        //noinspection JSUnresolvedVariable
        $.ajax({
            url: '/equipment/order/pre/?c=2&pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(dx){
                if(dx.res == 200){
                    if(dx.is_used){
                        last_used_action = 4;
                        last_used_pk = dx.pk;
                    }
                    else{
                        last_used_pk = dx.pk;
                        last_used_action = 3;
                    }
                }
                var x_holder = $('<div>');
                var b = $('<button>');
                var tb = $('<button>');
                var i = $('<i>');
                var s = $('<span>');
                var hd = $('<input>');
                var hs = $('<input>');
                hs.attr('name', 'seh').attr('type', 'hidden');
                hd.attr('type', 'hidden');
                hd.attr('name', 'ho');
                x_holder.addClass('btn-group');
                if(dx.is_used){
                    tb.addClass('btn-warning');
                    hs.val(dx.pk);
                }
                else{
                    tb.addClass('btn-default');
                    hd.val(dx.pk);
                }
                tb.addClass('btn btn-sm').append($('<i>').addClass('glyphicon glyphicon-hand-up')).attr('type', 'button').on('click', function(){
                    if(tb.hasClass('btn-default')){
                        $.ajax({
                            url: '/equipment/order/pre/?c=3&pk='+dx.pk,
                            method: 'get',
                            dataType: 'json',
                            success: function(dx2){
                                tb.removeClass('btn-default').addClass('btn-warning');
                                hs.val(dx2.pk);
                                hd.val('');
                            },
                            error: function(er){
                                $('#fAddOrderForTypes').find('.alert').removeClass('hidden').find('span').html(er.responseText);
                                setTimeout(function(){
                                    $('#fAddOrderForTypes').find('.alert').addClass('hidden');
                                }, 5000)
                            }
                        });

                    }
                    else{
                        $.ajax({
                            url: '/equipment/order/pre/?c=4&pk='+dx.pk,
                            method: 'get',
                            dataType: 'json',
                            success: function(){
                                tb.removeClass('btn-warning').addClass('btn-default');
                                hd.val(hs.val());
                                hs.val('');
                            },
                            error: function(er){
                                $('#fAddOrderForTypes').find('.alert').removeClass('hidden').find('span').html(er.responseText);
                                setTimeout(function(){
                                    $('#fAddOrderForTypes').find('.alert').addClass('hidden');
                                }, 5000);
                            }
                        });

                    }
                });
                i.addClass('glyphicon glyphicon-trash');
                s.addClass('hidden-sm hidden-xs').html(' '+r[0].name);
                //noinspection JSUnresolvedVariable
                b.addClass('btn btn-default btn-sm').append(i).append(s).attr('type', 'button');
                b.on('click', function(){
                    //noinspection JSUnresolvedVariable
                    $.ajax({
                        url: '/equipment/order/pre/?c=1&pk='+dx.pk,
                        method: 'get',
                        success: function(){
                            tb.removeClass('btn-warning').addClass('btn-default');
                            hs.val('').remove();
                            hd.remove();
                            x_holder.remove();
                        },
                        error: function(er){
                            post_error(er);
                        }
                    });
                });
                x_holder.append(b).append(tb).append(hs);
                $('#dOrders').removeClass('hidden').find('.panel-body').append(x_holder).append($('<span>').html('  ')).append(hd);
            },
            error: function(er){
                post_error(er);
            }
        });
    }).on('deselected', function(){

    }).on('loaded.rs.jquery.bootgrid', function(){
        $('[data-price=1]').priceFormat({
            thousandsSeparator: ',',
            suffix: '',
            clearPrefix: true,
            centsLimit: 0
        });
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url_prefix: "/equipment/type/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e,e2, r,summery) {
        summery.append(getActionArea());
        rebindModal(summery);
        bindDelete(summery);
        $('#bOrders').on('click', function(){
            xmb = $(this).data('pk');
            $('#fAddOrderForTypes').removeClass('hidden');
            document.location = '#dOrderContainer';
            sub.bootgrid('reload');
        });
        //noinspection JSUnresolvedVariable
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    });
    md.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        fd.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/equipment/type/rm/?pk='+btn.data('pk'),
                method: 'get',
                success: function(){
                    md.modal('hide');
                    reloadCurrent();
                },
                error: function(er){
                    post_error(er);
                }
            })
        });
    });
    ma.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        $('input').val('');
        if(btn.data('pk')!=undefined){
            $('[name=pk]').val(btn.data('pk'));
            $.ajax({
                url: '/equipment/type/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    $('[name=n]').val(d.name);
                },
                error: function(er){
                    post_error(er, null, ma);
                }
            })
        }
        fa.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/equipment/type/add/',
                method: 'post',
                data: fa.serialize(),
                success: function(){
                    ma.modal('hide');
                    reloadCurrent();
                },
                error: function(er){
                    post_error(er, null, ma);
                }
            })
        });
    });
});