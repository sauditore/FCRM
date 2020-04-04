$(function () {
    var srv = $('#tDService');
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    mad.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mad);
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/service/dedicate/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    mad.find('[name=n]').val(d.name).trigger('change');
                    mad.find('[name=pk]').val(d.ext);
                },
                error: function(er){
                    post_error(er.responseText);
                }
            });
        }
    });
    fad.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/service/dedicate/add/',
            method: 'post',
            data: fad.serialize(),
            success: function(){
                mad.modal('hide');
                reload_grid(srv);
            },
            error: function(er){
                post_error(er.responseText);
            }
        });
    });

    srv.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url: function () {
            return "/service/dedicate/";
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function (e, r) {
        $('[data-need-pk=1]').data('pk', r[0].ext).removeClass('hidden');
    });
});