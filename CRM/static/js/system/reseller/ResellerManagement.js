$(function () {
    var his = $('#tResellerHistory');
    $('[data-edit=1]').editable({

    });
    his.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url: function () {
            return "/user/reseller/history/?u="+$('#uid').val();
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        }
        //selection: true,
        //rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function (e, r) {
    });
});