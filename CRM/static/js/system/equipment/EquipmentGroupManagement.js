/**
 * Created by saeed on 12/9/2015.
 */
$(function(){
    var egm = $('#mAddNewEquipmentGroup');
    var egf = $('#fAddNewEquipmentGroup');
    var mch = $('#mChangeCounter');
    var fch = $('#fChangeCounter');
    mch.on('show.bs.modal', function(me){
        mch.find('[type=text]').val('');
        mch.find('[name=pk]').val($(me.relatedTarget).data('pk'));
    });
    fch.on('submit', function(fs){
        fs.preventDefault();
        var $this = $(this);
        $.ajax({
            url: $this.attr('action'),
            method: 'get',
            data: $this.serialize(),
            success: function(){
                mch.modal('hide');
                reloadCurrent();
            },
            error: function(er){
                post_error(er, null, mch);
            }
        });
    });
    initGrid({
        ajaxSettings:{
            method: 'get'
        },
        formatters: {
        },
        ajax: true,
        url_prefix: "/equipment/group/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function(e,e2, r, summery){
        summery.append(getActionArea());
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    });
    egm.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        var slc = $('#sTypes');
         var cs = $('#sCodes');
        cs.empty();
        slc.empty();
        egm.find('input').val('');
        $.ajax({
            url: '/equipment/type/?current=1&rowCount=-1',
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d.rows, function(a, b){
                    var o = $('<option>');
                    o.val(b.ext).html(b.name);
                    slc.append(o);
                });
            },
            error: function(er){
                post_error(er, null, egm);
            }
        });
        $.ajax({
            url: '/equipment/code/?current=1&rowCount=-1',
            dataType: 'json',
            method: 'get',
            success: function(d){
                $.each(d.rows, function(a,b){
                    var o = $('<option>');
                    o.val(b.ext).html(b.name);
                    cs.append(o);
                });
            },
            error: function(er){
                post_error(er, null, egm);
            }
        });
        if(btn.data('pk')!=undefined){
            $.ajax({
                method: 'get',
                dataType: 'json',
                url: '/equipment/group/j/?pk='+btn.data('pk'),
                success: function(d){
                    egm.find('[name=n]').val(d.name);
                    egm.find('[name=d]').val(d.description);
                    egm.find('[name=pk]').val(d.ext);
                    slc.val(d.type_id).change();
                    cs.val(d.code).change();
                },
                error: function(er){
                    post_error(er, null, egm);
                }
            });
        }
        egf.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                method: 'post',
                data: egf.serialize(),
                url: '/equipment/group/add/',
                success: function(){
                    egm.modal('hide');
                    reloadCurrent();
                    sAlert('عملیات با موفقیت انجام شد', 2);
                },
                error: function(er){
                    post_error(er, null, egm);
                }
            });
        });
    });

});