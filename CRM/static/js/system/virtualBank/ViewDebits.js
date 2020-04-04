/**
 * Created by saeed on 4/7/16.
 */

$(function () {
    $('[data-date=1]').persianDatepicker();
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {

            'price': function(c,r){
                if(c.id=='amount'){
                    return get_price_cell_formatter(r.amount, true, true);
                }
                else if(c.id == 'last_amount'){
                    return get_price_cell_formatter(r.last_amount, true, true);
                }
                return '';
            }
        },
        ajax: true,
        url_prefix: "/factor/debit/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e, e2, r, summery){
        var hst = $('#dDebitDetails').find('table').clone();
        if(hst.length){
            hst.bootgrid('destroy');
            hst.bootgrid({
                ajaxSettings: {
                    method: 'get'
                },
                formatters: {
                    'price2': function(c,r){
                        if(c.id=='old_value'){
                            return get_price_cell_formatter(r.old_value, true, true);
                        }
                        else if(c.id=='new_value'){
                            return get_price_cell_formatter(r.new_value, true, true);
                        }
                    },
                    'view_invoice': function(c,r){
                        if(r.invoice_id){
                            var a = $('<a>');
                            a.attr({'href': '/factor/show/all/?pk='+ r.invoice_id, 'target': '_blank'})
                            a.html(r.invoice_id);
                            return $('<div>').append(a).html();
                        }
                        return '';
                    }
                },
                ajax: true,
                url: "/factor/debit/history/j?u="+r[0].user__pk,
                labels: {
                    all: "همه",
                    infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
                    noResults: 'هیچ نتیجه ای وجود ندارد',
                    search: 'جستجو',
                    loading: 'درحال بارگزاری'
                },
                selection: true,
                rowSelect: true
            });
            summery.append($('<hr>'),hst);
        }
        var a = $('<div>').addClass('text-center').append(getActionArea());
        summery.append(a);
        rebindModal(summery);
        bindDelete(summery);
        summery.find('[data-need-pk]').data('pk', r[0].pk);
        summery.find('[data-need-cpk=1]').data('cpk', r[0].user__pk);
    });
});
