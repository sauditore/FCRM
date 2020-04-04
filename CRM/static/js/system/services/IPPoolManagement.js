$(function () {
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            user_nav: function(c,r){
                var a = $('<a>').attr({'href': '/user/nav/?uid='+ r.user_id}).html(r.first_name);
                return $('<div>').append(a).clone().html();
            },
            is_free: function(c,r){
                var i = $('<i>');
                var s = $('<span>');
                i.addClass('fa');
                s.append(i);
                if(r.is_free){
                    i.addClass('fa-check');
                    s.addClass('text-danger')
                }
                else{
                    i.addClass('fa-remove');
                    s.addClass('text-info');
                }
                return $('<div>').append(s).clone().html();
            },
            in_use: function(c,r){
                console.log(r.used);
                var i = $('<i>');
                var s = $('<span>');
                i.addClass('fa');
                s.append(i);
                if(r.used){
                    i.addClass('fa-check');
                    s.addClass('text-danger')
                }
                else{
                    i.addClass('fa-remove');
                    s.addClass('text-info');
                }
                return $('<div>').append(s).clone().html();
            }
        },
        ajax: true,
        url_prefix: "/service/ip/pool/",
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
        summery.find('[data-need-pk=1]').data('pk', r[0].pk);
        if(r[0].user_id != null){
            summery.find('[data-need-user=1]').removeClass('hidden');
            if(r[0].is_free){
                summery.find('[data-is-free=0]').removeClass('hidden');
                summery.find('[data-is-free=1]').addClass('hidden');
            }else{
                summery.find('[data-is-free=1]').removeClass('hidden');
                summery.find('[data-is-free=0]').addClass('hidden');
            }
        }
        bindDelete(summery);
    });
});