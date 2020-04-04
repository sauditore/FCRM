$(function () {
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url_prefix: "/indicator/pb/"
        ,
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true});
    getCurrentGrid().on('open.grid', function(e,w,r,summery){
        summery.append(getActionArea());
        rebindModal(summery);
        $('[data-need-pk=1]').data('pk', r[0].ext);
        bindDelete(summery);
    });
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    mad.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if(btn.data('pk') != undefined){
            $.ajax({
                url: '/indicator/pb/j/?pk='+btn.data('pk'),
                dataType: 'json',
                method: 'get',
                success: function(d){
                    mad.find('[name=n]').val(d.name);
                    mad.find('[name=pk]').val(d.ext);
                },
                error: function(er){
                    post_error(er.responseJSON.msg, er.responseJSON.param, mad);
                }
            });
        }
    });
    fad.on('submit', function(fs){
        fs.preventDefault();
        sAlert('آیا از تغییرات اطمینان دارید؟', 1, function(){
            $.ajax({
                method: 'post',
                data: fad.serialize(),
                url: '/indicator/pb/add/',
                success: function(){
                    reloadCurrent();
                    mad.modal('hide');
                    sAlert('تغییرات با موفقیت انجام شد',2);
                },
                error: function(er){
                    post_error(er.responseJSON.msg, er.responseJSON.param, mad);
                }
            });
        });
    });
});