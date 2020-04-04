$(function() {
    var fAdd = $('#fAddNewPopSite');
    initGrid({
        ajaxSettings:{
            method: 'get'
        },
        ajax: true,
        url_prefix: "/pops/?",
        labels: {
            all: "همه",
            infos: ""
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function(e,e2, r,summery){
        summery.append(getActionArea());
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].pk);
    });
    fAdd.off('submit').on('submit', function(fae){
        fae.preventDefault();
        $.ajax({
            url: '/pops/add/',
            method: 'post',
            data: fAdd.serialize(),
            success: function(){
                fAdd.find('input').val('');
                $('#mAddNewPopSite').modal('hide');
                reloadCurrent();
                sAlert('شبکه جدید با موفقیت اضافه شد', 2);
            },
            error: function(er){
                post_error(er);
            }
        });
    });
});