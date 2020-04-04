$(function () {
    var m_code = $('#mAddNewEquipmentCode');
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'price': function(c, r){
                var p = '';
                if(c.id == 'sell_price'){
                    p = r.sell_price;
                }
                if(c.id == 'used_sell_price'){
                    p = r.used_sell_price;
                }
                return '<span data-price=1>'+p+'</span>';
            }
        },
        ajax: true,
        url_prefix: "/equipment/code/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e,e2, r,summery) {
        summery.append(getActionArea());
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    }).on('loaded.grid', function(){
        $('[data-price=1]').priceFormat({
            thousandsSeparator: ',',
            suffix: '',
            clearPrefix: true,
            centsLimit: 0
        })
    });
    m_code.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        var mf = $('#fAddNewEquipmentCode');
        m_code.find('input').val('');
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: "/equipment/code/j/?pk="+btn.data('pk'),
                dataType: 'json',
                method: 'get',
                success:function(d){
                    m_code.find('[name=p]').val(d.code);
                    m_code.find('[name=sp]').val(d.sell_price);
                    m_code.find('[name=up]').val(d.used_sell_price);
                    m_code.find('[name=pk]').val(d.pk);
                    m_code.find('[name=n]').val(d.name);
                },
                error: function(er){
                    post_error(er, null, m_code);
                }
            });
        }
        mf.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: "/equipment/code/add/",
                method: 'post',
                data: mf.serialize(),
                success: function(){
                    m_code.modal('hide');
                    reloadCurrent();
                },
                error: function(er){
                   post_error(er, null, m_code);
                }
            })
        });
    });
});