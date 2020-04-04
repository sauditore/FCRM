$(function () {
    var mg = $('#mAddNewGroup');
    var fg = $('#fAddNewGroup');
    mg.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        clear_on_open(mg);
        mg.find('[name=pk]').val('');
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/service/float/option/group/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    mg.find('[name=pk]').val(btn.data('pk'));   // On success Load!
                    mg.find('[name=n]').val(d.name);
                    mg.find('[name=i]').val(d.view_order);
                    mg.find('[name=gh]').val(d.help);
                    mg.find('[name=ir]').prop('checked', d.is_required).trigger('change');
                    mg.find('[name=cr]').prop('checked', d.can_recharge).trigger('change');
                    mg.find('[name=mt]').val(d.metric).change();
                },
                error: function(er){
                    post_error(er,null, mg);
                }
            });
        }
        fg.off('submit').on('submit', function(fs){
            fs.preventDefault();
            mg.find('[type=submit]').addClass('m-progress');
            $.ajax({
                url: '/service/float/option/group/add/?',
                method: 'get',
                data: fg.serialize(),
                success: function(){
                    reloadCurrent();
                    mg.modal('hide');
                    sAlert('عملیات با موفقیت انجام شد', 2);
                },
                error: function(er){
                    post_error(er,null, mg);
                }
            });
        });
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'req': function(c,r){
                var i = $('<i>').addClass('fa');
                var x = false;
                if(c.id=='is_required'){
                    x = r.is_required;
                }
                else{
                    x = r.can_recharge;
                }
                if(x){
                    i.addClass('fa-check text-primary');
                }
                else{
                    i.addClass('fa-remove text-danger');
                }
                return $('<div>').append(i).html();
            }
        },
        ajax: true,
        url_prefix: "/service/float/option/group/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e,e2, r, summery) {
        summery.append(getActionArea());
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    });
});
