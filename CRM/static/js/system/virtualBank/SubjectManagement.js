/**
 * Created by saeed on 4/13/16.
 */
$(function (){
    $('#mEditSubject').on('show.bs.modal', function(mx){
        var m = $(mx.target);
        clear_on_open(m);
        var b = $(mx.relatedTarget);
        var sf = $('#fEditSubject');
        m.find('[name=s]').val(b.data('pk'));
        sf.off('submit');
        sf.on('submit', function(s){
            s.preventDefault();
            $.ajax({
                url: "/factor/debit/subject/e/",
                method: 'post',
                data: sf.serialize(),
                success: function(){
                    reloadCurrent();
                    m.modal('hide');
                    sAlert('تغییرات با موفقیت انجام شد',2);
                },
                error: function(er){
                    post_error(er, null, m);
                }
            });
        });
        if(b.data('pk')!=undefined){
            $.ajax({
                url: "/factor/debit/subject/e/?s=" + b.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    m.find('[name=n]').val(d.name);
                    m.find('[name=d]').val(d.des);
                },
                error: function(er){
                    post_error(er, null, m);
                }
            });
        }
    });
    initGrid({
        ajaxSettings:{
            method: 'get'
        },
        ajax: true,
        url_prefix: '/factor/debit/subject/',
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function(e,e2, r,summery){
        summery.append(getActionArea());
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].pk);
    });
});