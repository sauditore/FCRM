$(function () {
    var eq = $('#tEquipment');
    var fa = $('#fAddNewEquipment');
    var ma = $('#mAddNewEquipment');
    var fr = $('#fChangeEquipmentState');
    var mr = $('#mChangeEquipmentState');
    var mhi = $('#mEquipmentAmountChange');
    $('#bHistory').off('click').on('click', function(){
        document.location = '/equipment/order/?eqe='+$('#bHistory').data('pk');
    });
    mhi.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        var tbl = $('#tEquipmentChange').find('tbody');
        tbl.empty();
        $.ajax({
            url: '/equipment/change/?pk='+btn.data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d.data, function(a,b){
                    var tr = $('<tr>');
                    var td0 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    td0.html(b.pk);
                    td2.html(b.change);
                    td1.html(b.update_date);
                    tr.append(td0).append(td1).append(td2);
                    tbl.append(tr);
                });
            },
            error: function(er){
                post_error(er,null, mhi);
            }
        })
    });
    mr.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mr.find('input').val('');
        mr.find('[name=pk]').val(btn.data('pk'));
        $.ajax({
            url: '/equipment/state/?current=1&rowCount=-1',
            method: 'get',
            dataType: 'json',
            success: function(d){
                var slc = $('#sEQStates');
                slc.empty();
                $.each(d.rows, function(a,b){
                    var o = $('<option>');
                    o.val(b.ext).html(b.name);
                    slc.append(o);
                });
            },
            error: function(er){
                post_error(er, null, mr);
            }
        });
        fr.off('submit').on('submit', function(fs){
            fs.preventDefault();
            fr.find('[type=submit]').addClass('m-progress');
            $.ajax({
                method: 'post',
                url: '/equipment/return/',
                data: fr.serialize(),
                success: function(){
                    mr.modal('hide');
                    reselectCurrent();
                    sAlert('بازگشت به انبار انجام شد', 2);
                },
                error: function(er){
                    post_error(er, null,fr);
                }
            });
        });
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'bool_tran': function(c, r){
                var dc = c.id;
                var dr = false;
                if(dc=='is_used'){
                    dr = r.is_used
                }
                else if(dc=='is_involved'){
                    dr = r.is_involved;
                }
                if(dr){
                    return 'بلی';
                }
                else{
                    return 'خیر';
                }

            }
        },
        ajax: true,
        url_prefix:"/equipment/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e,e2, r, summery) {
        summery.append(getActionArea());
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
        var brt = $('#bReturn');
        var bus = $('#bUsed');
        $.ajax({
            url: '/equipment/detail/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                if(d.can_return){
                    brt.removeClass('hidden');
                    brt.data('pk', r[0].ext);
                }
                else{
                    brt.addClass('hidden').data('pk', '');
                }
                if(d.is_used){
                    bus.removeClass('btn-info').addClass('btn-warning');
                }
                else{
                    bus.removeClass('btn-warning').addClass('btn-info')
                }
                if(d.can_mark_used){
                    bus.removeClass('hidden').data('pk', r[0].ext);
                }
                else{
                    bus.addClass('hidden').data('pk', '');
                }
                rebindModal(summery);
                bindDelete(summery);
            },
            error: function (er) {
                post_error(er, null);
            }
        });
        bus.off('click').on('click', function(be){
            $.ajax({
                url: '/equipment/toggle_used/?pk='+r[0].ext,
                method: 'get',
                success: function(){
                    reselectCurrent();
                },
                error: function(er){

                }
            });
        });
    });
    ma.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        var s = $('#sCode');
        var g = $('#sGroups');
        ma.find('input').val('');
        $.ajax({
            url: '/equipment/group/?current=1&rowCount=-1',
            method: 'get',
            dataType: 'json',
            success: function(d){
                g.empty();
                $.each(d.rows, function(a,b){
                    var o = $('<option>');
                    o.val(b.ext).html(b.name);
                    g.append(o);
                });
            },
            error: function(er){
                post_error(er, null, ma);
            }
        });
        if(btn.data('pk')!=undefined){
            $('[name=pk]').val(btn.data('pk'));
            $.ajax({
                url: '/equipment/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    $('[name=s]').val(d.serial);
                    $('[name=d]').val(d.description);
                    g.val(d.group);
                },
                error: function(er){
                    post_error(er, null, ma);
                }
            });
        }
        fa.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/equipment/add/',
                method: 'post',
                data: fa.serialize(),
                success: function(){
                    ma.modal('hide');
                    reloadCurrent();
                    sAlert('عملیات با موفقیت انجام شد',2);
                },
                error: function(er){
                    post_error(er, null, ma);
                }
            });
        });
    });
});