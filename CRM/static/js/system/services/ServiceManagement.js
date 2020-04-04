/**
 * Created by saeed on 4/7/16.
 */

$(function () {
    var mad = $('#msc');
    var fad = mad.find('form');
    mad.on('show.bs.modal', function (me) {
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if (btn.data('pk') != undefined) {
            $.ajax({
                method: 'get',
                url: '/service/j/?pk=' + btn.data('pk'),
                dataType: 'json',
                success: function (d) {
                    mad.find('[name=pk]').val(d.pk);
                    mad.find('[name=n]').val(d.name);
                    mad.find('[name=d]').val(d.description);
                    mad.find('[name=isn]').prop('checked', d.is_visible);
                    mad.find('[name=gn]').val(d.selected_group).change();
                    mad.find('[name=gt]').val(d.group_type).change();
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
            url: '/service/create/',
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
            'visible': function(c,r){
                var i = $('<i>').addClass('fa');
                var d = $('<div>').append(i);
                if(r.is_visible==true){
                    i.addClass('fa-check text-success');
                }
                else{
                    i.addClass('fa-remove text-danger');
                }
                return d.html();
            }
        },
        ajax: true,
        url_prefix: "/service/show/all/",
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
        bindDelete(summery);
        var lnk = summery.find('[data-action=link]');
        lnk.attr('href', lnk.attr('href')+r[0].pk);
        summery.find('[data-need-pk]').data('pk', r[0].ext);
    });
});
