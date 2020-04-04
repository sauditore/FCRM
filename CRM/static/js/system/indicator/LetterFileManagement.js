$(function () {
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    mad.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/indicator/lf/j/?pk='+btn.data('pk'),
                dataType: 'json',
                method: 'get',
                success: function(d){
                    mad.find('[type=hidden]').val(d.ext);
                    mad.find('[name=n]').val(d.name);
                },
                error: function (er) {
                    post_error(er.responseJSON.msg, er.responseJSON.param, mad);
                }
            });
        }
    });
    fad.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/indicator/lf/add/',
            method: 'post',
            data: fad.serialize(),
            success: function(){
                mad.modal('hide');
                reloadCurrent();
            },
            error: function(er){
                post_error(er.responseJSON.msg, er.responseJSON.param, mad);
            }
        });
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url_prefix: "/indicator/lf/",
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
        $('[data-need-pk=1]').data('pk', r[0].ext);
        rebindModal(summery);
        bindDelete(summery);
    });
});