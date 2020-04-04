$(function () {
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    mad.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if(btn.data('pk') != undefined){
            $.ajax({
                url: '/factor/dedicate/send/type/j/?pk='+btn.data('pk'),
                dataType: 'json',
                method: 'get',
                success: function(d){
                    mad.find('[name=n]').val(d.name);
                    mad.find('[name=pk]').val(d.ext);
                },
                error: function(er){
                    post_error(er.responseText);
                }
            });
        }
        fad.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/factor/dedicate/send/type/add/',
                method: 'post',
                data: fad.serialize(),
                success: function(){
                    mad.modal('hide');
                    reloadCurrent();
                    sAlert('عملیات با موفقیت انجام شد', 2);
                },
                error: function(er){
                    post_error(er.responseText);
                }
            });
        });
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url_prefix: "/factor/dedicate/send/type/",
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
        summery.append(getActionArea());
        bindDelete(summery);
        rebindModal(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    });
});