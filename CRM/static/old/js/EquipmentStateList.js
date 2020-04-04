$(function () {
    var est = $('#tEquipmentStateList');
    var f = $('#fAddEquipmentStateList');
    var m = $('#mAddEquipmentStateList');
    var md = $('#mDeleteEquipmentStateList');
    var fd = $('#fDeleteEquipmentStateList');
    est.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url: function () {
            return "/equipment/state/";
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
        $('[data-need-pk=1]').data('pk', r[0].ext).removeClass('hidden');
    });
    m.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        m.find('input').val('');
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/equipment/state/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function (d) {
                    m.find('[name=pk]').val(d.pk);
                    m.find('[name=n]').val(d.name);
                    m.find('[name=d]').val(d.description);
                },
                error: function(er){
                    m.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        m.find('.alert').addClass('hidden');
                    }, 5000);
                }
            });
        }
        f.off('submit').on('submit', function(fe){
            fe.preventDefault();
            f.find('[type=submit]').button('loading');
            $.ajax({
                url: '/equipment/state/add/',
                method: 'post',
                data: f.serialize(),
                success: function(){
                    m.modal('hide');
                    est.bootgrid('reload');
                    f.find('[type=submit]').button('reset');
                },
                error: function(er){
                    m.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        f.find('[type=submit]').button('reset');
                        m.find('.alert').addClass('hidden');
                    }, 5000)
                }
            });
        });
    });
    md.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        fd.off('submit').on('submit', function(fe){
            fe.preventDefault();
            fd.find('[type=submit]').button('loading');
            $.ajax({
                url: '/equipment/state/rm/?pk='+btn.data('pk'),
                method: 'get',
                success: function(){
                    md.modal('hide');
                    fd.find('[type=submit]').button('reset');
                    est.bootgrid('reload');
                },
                error: function(er){
                    md.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        fd.find('[type=submit]').button('reset');
                        md.find('.alert').addClass('hidden');
                    }, 5000);
                }
            });
        });

    });
});