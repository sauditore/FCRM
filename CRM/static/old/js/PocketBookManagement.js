$(function () {
    var tpm = $('.table');
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
        $.ajax({
            method: 'post',
            data: fad.serialize(),
            url: '/indicator/pb/add/',
            success: function(){
                reload_grid(tpm);
                mad.modal('hide');
            },
            error: function(er){
                post_error(er.responseJSON.msg, er.responseJSON.param, mad);
            }
        })
    });
    tpm.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url: function () {
            return "/indicator/pb/";
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