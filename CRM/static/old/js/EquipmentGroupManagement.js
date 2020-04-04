/**
 * Created by saeed on 12/9/2015.
 */
$(function(){
    var eqg = $('#tEQGroups');
    var egm = $('#mAddNewEquipmentGroup');
    var egf = $('#fAddNewEquipmentGroup');
    var egd = $('#mDeleteEquipmentGroup');
    var egs = $('#fDeleteEquipmentGroup');
    egd.off().on('show.bs.modal', function (ege) {
        var btn = $(ege.relatedTarget);
        egd.find('.alert').addClass('hidden');
        egs.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/equipment/group/rm/?g='+btn.data('pk'),
                method: 'get',
                success: function(){
                    eqg.bootgrid('reload');
                    egd.modal('hide');
                },
                error: function(er){
                    egd.find('.alert').removeClass('hidden').html(er.responseText);
                    setTimeout(function(){
                        egd.find('.alert').addClass('hidden');
                    }, 5000)
                }
            });
        });
    });
    eqg.bootgrid({
        ajaxSettings:{
            method: 'get'
        },
        formatters: {
        },
        ajax: true,
        url: function(){
            return "/equipment/group/";
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function(e, r){
        $('[data-need-pk=1]').data('pk', r[0].ext).removeClass('hidden');
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
                egm.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                setTimeout(function(){
                    egm.find('.alert').addClass('hidden');
                }, 5000);
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
                console.log(er.responseText);
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
                    slc.val(d.type_id);
                    cs.val(d.code);
                },
                error: function(er){
                    egm.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        egm.find('.alert').addClass('hidden');
                    }, 5000);
                }
            });
        }
        egm.find('.alert').addClass('hidden');
        egf.off('submit').on('submit', function(fs){
            fs.preventDefault();
            egf.find('[type=submit]').addClass('m-progress');
            $.ajax({
                method: 'post',
                data: egf.serialize(),
                url: '/equipment/group/add/',
                success: function(){
                    eqg.bootgrid('reload');
                    egm.modal('hide');
                    egm.find('input').val('');
                    egf.find('[type=submit]').removeClass('m-progress');
                },
                error: function(er){
                    egm.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        egm.find('.alert').addClass('hidden');
                        egf.find('[type=submit]').removeClass('m-progress');
                    }, 5000);
                }
            });
        });
    });

});