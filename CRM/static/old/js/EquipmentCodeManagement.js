$(function () {
    var eqg = $('#tEquipmentCode');
    var m_code = $('#mAddNewEquipmentCode');
    var m_del = $('#mDelEquipmentCode');
    eqg.bootgrid({
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
        url: function () {
            return "/equipment/code/";
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function (e, r) {
        $('[data-need-pk=1]').data('pk', r[0].ext).removeClass('hidden');
    }).on('loaded.rs.jquery.bootgrid', function(){
        $('[data-price=1]').priceFormat({
            thousandsSeparator: ',',
            suffix: '',
            clearPrefix: true,
            centsLimit: 0
        })
    });
    m_del.on('show.bs.modal', function(me){
        var f = $('#fDelEquipmentCode');
        var b = $(me.relatedTarget);
        f.off('submit').on('submit', function(fs){
            fs.preventDefault();
            f.find('[type=submit]').button('loading');
            $.ajax({
                url: '/equipment/code/rm/?pk='+ b.data('pk'),
                method: 'get',
                success: function(){
                    m_del.modal('hide');
                    f.find('[type=submit]').button('reset');
                    eqg.bootgrid('reload');
                },
                error: function(er){
                    m_del.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        m_del.find('.alert').addClass('hidden');
                        f.find('[type=submit]').button('reset');
                    }, 5000);
                }
            });
        });
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
                    m_code.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        m_code.find('.alert').addClass('hidden');
                    }, 5000)
                }
            });
        }
        mf.off('submit').on('submit', function(fs){
            fs.preventDefault();
            m_code.find('[type=submit]').button('loading');
            $.ajax({
                url: "/equipment/code/add/",
                method: 'post',
                data: mf.serialize(),
                success: function(){
                    m_code.find('[type=submit]').button('reset');
                    m_code.modal('hide');
                    eqg.bootgrid('reload');
                },
                error: function(er){
                    m_code.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        m_code.find('.alert').addClass('hidden');
                        m_code.find('[type=submit]').button('reset');
                    }, 5000);
                }
            })
        });
    });
});