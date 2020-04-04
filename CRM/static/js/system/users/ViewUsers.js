$(function () {
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'is_active': function(c,r){
                var i = $('<i>');
                if(r.user__is_active){
                    i.addClass('fa fa-check text-info');
                }
                else{
                    i.addClass('fa fa-remove text-danger');
                }
                return $('<div>').append(i).html();
            }
        },
        ajax: true,
        url_prefix: "/user/view/?t="+$('#hut').val(),
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e, e2, r) {
        document.location = '/user/nav/?uid='+r[0].user__pk;
    });
});
