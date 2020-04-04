$(function () {
    var orders = $('#tOrders');
    var ma = $('#mAcceptEquipmentOrder');
    var fa = $('#fAcceptEquipmentOrder');
    var tA = $('#tAcceptOrder');
    var mr = $('#mRejectOrderModal');
    var fr = $('#fRejectOrderModal');
    var tAU = '';
    var md = $('#mDeliverOrder');
    var fd = $('#fDeliverOrder');
    var sch = $('#fSearchArea');
    sch.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $('#searchData').val(sch.serialize());
        orders.bootgrid('reload');
    });
    var fCo = $('#fCommitDelivery');
    var mCo = $('#mCommitDelivery');
    mCo.on('show.bs.modal', function(me){
        var bx = $(me.relatedTarget);
        mCo.find('[name=o]').val(bx.data('o'));
        mCo.find('[name=e]').val(bx.data('e'));
    });
    fCo.off('submit').on('submit', function(fs){
        fs.preventDefault();
        fCo.find('[type=submit]').addClass('m-progress');
          $.ajax({
            url: '/equipment/order/checkout/?',
            data: fCo.serialize(),
            method: 'get',
            success: function(){
                mCo.find('textarea').html('');
                mCo.modal('hide');
                fCo.find('[type=submit]').removeClass('m-progress');
                reselect();
            },
            error: function(er){
                fCo.find('[type=submit]').removeClass('m-progress');
            }
        })
    });
    md.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        md.find('[name=pk]').val(btn.data('pk'));
        fd.off('submit').on('submit', function(fs){
            fs.preventDefault();
            md.find('[type=submit]').addClass('m-progress');
            $.ajax({
                url: '/equipment/order/deliver/',
                method: 'post',
                data: fd.serialize(),
                success: function(){
                    md.modal('hide');
                    reselect();
                    md.find('[type=submit]').removeClass('m-progress');
                },
                error: function(er){
                    md.find('.alert').removeClass('hidden fadeOut').addClass('animated wobble').find('span').html(er.responseText);
                    setTimeout(function(){
                        md.find('[type=submit]').removeClass('m-progress');
                        md.find('.alert').removeClass('wobble').addClass('fadeOut');
                        setTimeout(function(){
                            md.find('.alert').addClass('hidden');
                        }, 1000);
                    }, 5000);


                }
            });
        });
    });
    var bStart = $('#bStart');
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
    bStart.off('click').on('click', function(){
        bStart.addClass('m-progress');
        $.ajax({
            method: 'get',
            url: '/equipment/order/start/?pk='+bStart.data('pk'),
            success: function(){
                reselect();
                bStart.removeClass('m-progress');
            },
            error: function(er){
                bStart.removeClass('m-progress');
                $('#dvDetailContainer').find('.alert').removeClass('hidden fadeOut').addClass('animated shake').find('.text-danger').html(er.responseText);
            }
        });
    });
    function reselect(){
        var x1 = orders.bootgrid('getSelectedRows');
        orders.bootgrid('deselect');
        orders.bootgrid('select', x1);
    }
    mr.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mr.find('[name=pk]').val(btn.data('pk'));
        mr.find('.alert').find('button').off().on('click', function(){
            mr.find('.alert').removeClass('shake').addClass('animated fadeOut');
        });
        fr.off('submit').on('submit', function(fs){
            fs.preventDefault();
            fr.find('[type=submit]').addClass('m-progress');
            $.ajax({
                url: '/equipment/order/reject/',
                data: fr.serialize(),
                method: 'post',
                success: function(){
                    fr.find('[type=submit]').removeClass('m-progress');
                    mr.modal('hide');
                    reselect();
                },
                error: function (er) {
                    fr.find('[type=submit]').removeClass('m-progress');
                    mr.find('.alert').removeClass('fadeOut hidden').addClass('animated shake').find('.text-danger').html(er.responseText);
                }
            });
        });
    });
    ma.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        tAU = btn.data('pk');
        ma.find('[name=pk]').val(btn.data('pk'));

        tA.bootgrid({
            ajaxSettings: {
                method: 'get'
            },
            formatters: {
                'trans_bool': function(c,r){

                    if(r.is_processing){
                        return 'بلی'
                    }
                    else{
                        return 'خیر'
                    }
                }
            },
            ajax: true,
            url: function () {
                return "/equipment/order/select/?pk="+tAU;
            },
            labels: {
                all: "همه",
                infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
                noResults: 'هیچ نتیجه ای وجود ندارد',
                search: 'جستجو'
            },
            selection: true,
            rowSelect: true
        }).off('selected.rs.jquery.bootgrid').on('selected.rs.jquery.bootgrid', function(e,r){
            ma.find('input[name=eq]').val(r[0].ext);
        });
        tA.bootgrid('reload');
        ma.find('.alert').find('button').off().on('click', function(){
            ma.find('.alert').removeClass('shake').addClass('animated fadeOut');
        });

        fa.off('submit').on('submit', function(fs){
            fs.preventDefault();
            fa.find('[type=submit]').addClass('m-progress');
            $.ajax({
                url: '/equipment/order/equipment/',
                method: 'post',
                data: fa.serialize(),
                success: function(){
                    ma.modal('hide');
                    ma.find('[type=submit]').removeClass('m-progress');
                    reselect();
                },
                error: function(er){
                    ma.find('[type=submit]').removeClass('m-progress');
                    ma.find('.alert').removeClass('fadeOut hidden').addClass('shake animated').find('.text-danger').html(er.responseText);
                }
            });
        });
    }).on('hide.bs.modal', function(){
        ma.find('.alert').removeClass('animated');
        tA.bootgrid('clear');
    });
    orders.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'trans_bool': function(c,r){
                var cid = c.id;
                var data = false;
                if(cid=='is_processing'){
                    data= r.is_processing;
                }
                else if(cid=='order__is_borrow'){
                    data= r.is_borrow;
                }
                if(data){
                    return 'بلی'
                }
                else{
                    return 'خیر'
                }
            }
        },
        ajax: true,
        url: function () {
            return "/equipment/order/?"+$('#searchData').val();
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function (e, r) {
        //$('[data-need-pk=1]').data('pk', r[0].ext).removeClass('hidden');
        var dc = $('#dvDetailContainer');
        dc.find('.alert').find('button').off().on('click', function(){
            dc.find('.alert').removeClass('shake').addClass('fadeOut');
        });
        var tb = $('#tOrderDetails').find('tbody');
        tb.empty();
        $.ajax({
            url: '/equipment/order/detail/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                if(d.can_start){
                    $('#bStart').removeClass('hidden');
                }
                else{
                    $('#bStart').addClass('hidden');
                }
                if(d.can_deliver){
                    $('#bDeliver').removeClass('hidden');
                }
                else{
                    $('#bDeliver').addClass('hidden');
                }
                $('[data-need-pk=1]').data('pk', d.main_order);
                tb.empty();
                $.each(d.data, function(a, b){
                    var tr = $('<tr>');
                    var td0 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    var td3 = $('<td>');
                    var td4 = $('<td>');
                    var td5 = $('<td>');
                    var td6 = $('<td>');
                    var td7 = $('<td>');
                    //var td3 = $('<td>');
                    if(b.is_used){
                        td7.html("بلی");
                    }
                    else{
                        td7.html("خیر");
                    }
                    var b1 = $('<button>');
                    var i2 = $('<i>');
                    var s = $('<span>');
                    var br = $('<button>');
                    var sr = $('<span>');
                    var ir = $('<i>');
                    var bInstall = $('<button>');
                    var bNotInstall = $('<button>');
                    var bCheckOut = $('<button>');
                    // INSTALL COMPONENTS
                    var iInstall = $('<i>');
                    var sInstall = $('<span>');
                    var sSpace = $('<span>');
                    sSpace.append('  ');
                    iInstall.addClass('glyphicon glyphicon-saved');
                    sInstall.addClass('hidden-sm hidden-xs').html(' نصب');
                    bInstall.addClass('btn btn-sm btn-info').attr('type', 'button').append(iInstall).append(sInstall).on('click', function(){
                        $.ajax({
                            url: '/equipment/order/checkout/?s=1&e='+ b.fk_equipment_order_detail_order_item__equipment__ext+'&o='+ b.ext,
                            method: 'get',
                            success: function(){
                                reselect();
                            },
                            error: function(){

                            }
                        })
                    });
                    // NOT INSTALLED COMPONENTS
                    //var iNotInstall = $('<i>');
                    //var sNotInstall = $('<span>');
                    //iNotInstall.addClass('glyphicon glyphicon-remove');
                    //sNotInstall.addClass('hidden-sm hidden-xs').html(' برگشتی');
                    //bNotInstall.addClass('btn btn-warning btn-sm').attr('type', 'button').append(iNotInstall).append(sNotInstall).on('click', function(){
                    //    $.ajax({
                    //        url: '/equipment/order/checkout/?s=nana&e='+ b.fk_equipment_order_detail_order_item__equipment__ext+'&o='+ b.ext,
                    //        method: 'get',
                    //        success: function(){
                    //            reselect();
                    //        },
                    //        error: function(){
                    //
                    //        }
                    //    })
                    //});
                    // CHECKOUT COMPONENTS
                    var iCheckout = $('<i>');
                    var sCheckout = $('<span>');
                    iCheckout.addClass('glyphicon glyphicon-export');
                    sCheckout.addClass('hidden-sm hidden-xs').html(' تسویه');
                    bCheckOut.addClass('btn btn-success btn-sm').attr('type', 'button').append(iCheckout).append(sCheckout).attr('data-target', '#mCommitDelivery').attr('data-toggle', 'modal').attr('data-e', b.fk_equipment_order_detail_order_item__equipment__ext).attr('data-o', b.ext);

                    td0.html(b.pk);
                    td1.html(b.equipment__name);
                    td2.html(b.fk_equipment_order_detail_order_item__equipment__serial);
                    i2.addClass('glyphicon glyphicon-check');
                    s.addClass('hidden-sm hidden-xs').html(' پذیرش');
                    b1.addClass('btn btn-info btn-sm').append(i2).append(s);
                    b1.attr('data-toggle', 'modal').attr('data-target', '#mAcceptEquipmentOrder').attr('data-pk', b.ext);
                    ir.addClass('glyphicon glyphicon-trash');
                    sr.addClass('hidden-sm hidden-xs').html('  حذف');
                    br.addClass('btn btn-danger btn-sm').append(ir).append(sr);
                    br.attr('data-toggle', 'modal').attr('data-target', '#mRejectOrderModal').attr('data-pk', b.ext);
                    //td6.append(b1);
                    var is_rejected = 'خیر';
                    if(b.is_accepted){
                        if(b.fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__is_installed === true && !b.fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__checkout_date){
                            if(d.can_checkout){
                                td6.append(bCheckOut);
                            }
                        }
                        else if(b.fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__is_installed === null){
                            if(d.can_install){
                                td6.append(bInstall).append(sSpace);
                            }
                            //if(d.can_return){
                            //    td6.append(bNotInstall);
                            //}
                        }
                        else{
                            td6.html(b.fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__comment);
                        }
                        //td6.append(br);
                    }
                    else if(b.is_rejected){
                        //is_rejected = 'بلی';
                        is_rejected = b.reason;
                        //td6.append(b1);
                    }
                    else if (d.can_accept){
                        td6.append(b1).append($('<span>').html('  ')).append(br);
                    }

                    td4.html(is_rejected);
                    td5.html(b.change_date);
                    tr.append(td0).append(td1).append(td2).append($('<td>').html(b.fk_equipment_order_detail_order_item__fk_equipment_borrow_order__property_number)).append(td4).append(td5).append(td7).append(td6);
                    tb.append(tr);
                });
            },
            error: function(er){
                dc.find('.alert').removeClass('fadeOut hidden').addClass('animated shake').find('.text-danger').html(er.responseText);
            }
        })
    });

});