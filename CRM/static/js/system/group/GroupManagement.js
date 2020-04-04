/**
 * Created by saeed on 4/7/16.
 */

$(function(){
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    mad.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if(btn.data('pk')!=undefined){
            $.ajax({
                method: 'get',
                url: '/groups/j/?pk='+btn.data('pk'),
                dataType: 'json',
                success: function(d){
                    mad.find('[name=n]').val(d.name);
                    mad.find('[name=pk]').val(d.pk);
                },
                error: function(er){
                    show_error(er.responseText);
                }
            });
        }
    });
    fad.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/groups/add/',
            method: 'post',
            data: fad.serialize(),
            success: function(){
                mad.modal('hide');
                reloadCurrent();
                sAlert('تغییرات با موفقیت انجام شد', 2);
            },
            error: function(er){
                post_error(er.responseJSON.msg, er.responseJSON.param, mad);
            }
        })
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
        },
        ajax: true,
        url_prefix: "/groups/show/all/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function(e, e2, r, summery){
        var a = $('<div>').addClass('text-center').append(getActionArea());
        summery.append(a);
        rebindModal(summery);
        summery.find('[data-need-pk]').data('pk', r[0].pk);
        bindDelete(summery);
        summery.find('[data-link=1]').on('click', function(ae){
            ae.preventDefault();
            document.location = $(this).data('url')+'?g='+$(this).data('pk');
        })
    });
});
