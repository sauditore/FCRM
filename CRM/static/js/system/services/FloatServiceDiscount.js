/**
 * Created by saeed on 4/7/16.
 */

$(function () {
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    mad.on('show.bs.modal', function (me) {
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if (btn.data('pk') != undefined) {
            $.ajax({
                method: 'get',
                url: '/service/float/discount/j/?pk=' + btn.data('pk'),
                dataType: 'json',
                success: function (d) {
                    mad.find('[name=pk]').val(d.ext);
                    mad.find('[name=n]').val(d.name);
                    mad.find('[name=c]').val(d.charge);
                    mad.find('[name=e]').val(d.extra);
                    mad.find('[name=p]').val(d.extra_package);
                },
                error: function (er) {
                    post_error(er, null, mad);
                }
            });
        }
    });
    fad.on('submit', function (fs) {
        fs.preventDefault();
        $.ajax({
            url: '/service/float/discount/add/',
            method: 'post',
            data: fad.serialize(),
            success: function () {
                mad.modal('hide');
                reloadCurrent();
                sAlert('تغییرات با موفقیت انجام شد', 2);
            },
            error: function (er) {
                post_error(er, null, mad);
            }
        })
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url_prefix: "/service/float/discount/",
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
        var a = $('<div>').addClass('text-center').append(getActionArea());
        summery.append(a);
        rebindModal(summery);
        summery.find('[data-need-pk]').data('pk', r[0].ext);
        bindDelete(summery);
    });
});
