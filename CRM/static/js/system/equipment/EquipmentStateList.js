$(function () {
    var f = $('#fAddEquipmentStateList');
    var m = $('#mAddEquipmentStateList');
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url_prefix: "/equipment/state/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e, e2, r, summery) {
        summery.append(getActionArea());
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    });
    m.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(m);
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
                    post_error(er, null, m);
                }
            });
        }
        f.off('submit').on('submit', function(fe){
            fe.preventDefault();
            $.ajax({
                url: '/equipment/state/add/',
                method: 'post',
                data: f.serialize(),
                success: function(){
                    m.modal('hide');
                    reloadCurrent();
                    sAlert('عملیات با موفقیت انجام شد', 2);
                },
                error: function(er){
                    post_error(er, null,m);
                }
            });
        });
    });
});