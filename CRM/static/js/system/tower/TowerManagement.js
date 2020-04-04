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
                url: '/tower/j/?pk=' + btn.data('pk'),
                dataType: 'json',
                success: function (d) {
                    mad.find('[name=pk]').val(d.pk);
                    mad.find('[name=n]').val(d.name);
                    mad.find('[name=d]').val(d.description);
                    mad.find('[name=ad]').val(d.address);
                    mad.find('[name=mb]').val(d.max_bw);
                    mad.find('[name=ht]').prop('checked', d.has_test);

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
            url: '/tower/add/',
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
        formatters: {
            'has_test': function(c,r){
                var l = $('<label>').addClass('label');
                var i = $('<i>').addClass('fa');
                if(r.has_test){
                    l.addClass('label-danger');
                    i.addClass('fa-check');
                }else{
                    l.addClass('label-info');
                    i.addClass('fa-remove');
                }
                l.append(i);
                return $('<div>').append(l).html()
            }
        },
        ajax: true,
        url_prefix: "/tower/",
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
        summery.find('[data-need-pk]').data('pk', r[0].pk);
        bindDelete(summery);
    });
});
