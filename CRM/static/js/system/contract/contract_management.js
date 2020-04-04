$(function(){
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'sniper': function(c,r){
                return r.body.substr(0, 50);
            }
        },
        ajax: true,
        url_prefix: "/contract/"
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
});
