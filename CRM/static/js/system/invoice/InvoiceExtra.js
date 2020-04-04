
$(function(){
    $('#bToday').on('click', function(){
        $.ajax({
            url: '/factor/today_sell/',
            method: 'get',
            dataType: 'json',
            success: function(d){
                var x = get_price_cell_formatter;
                $('[data-col=0]').empty().append($('<span>').addClass('price').html(x(d.sell, true)));
                $('[data-col=1]').empty().append($('<span>').addClass('price').html(x(d.packages, true)));
                $('[data-col=2]').empty().append($('<span>').addClass('price').html(x(d.package_payment, true)));
                $('[data-col=3]').empty().append($('<span>').addClass('price').html(x(d.today_recharge, true)));
                $('[data-col=4]').empty().append($('<span>').addClass('price').html(x(d.recharge_payment, true)));
                $('[data-col=5]').empty().append($('<span>').addClass('price').html(x(d.bank_payment)));
            },
            error: function(er){
                post_error(er, null, $(this));
            }
        });
    });
    $('#bAnalyze').on('click', function(){
        $.ajax({
            url: '/factor/analyse/',
            dataType: 'json',
            method: 'get',
            data: $('#fSearch').serialize(),
            success: function(d){
                var x = get_price_cell_formatter;
                $('#sMostSell').html(d.max_sell[0]);
                $('#sMostSellData').html(x(d.max_sell[1], true));
                $('#sMostRechargeDate').html(d.max_recharges[0]);
                $('#sMostRecharge').html(x(d.max_recharges[1], true));
                $('#sMostPackages').html(d.max_packages[0]);
                $('#sMostPackagesDate').html(x(d.max_packages[1], true));
                $('#sTotalInvoice').html(d.invoice_count);
                $('#sOnlinePayment').html(d.online_payments);
                $('#sOnlinePaymentAmount').html(x(d.online_payments_amount, true));
                $('#sPersonnelPayment').html(d.personnel_payments);
                $('#sPersonnelPaymentAmount').html(x(d.personnel_payments_amount, true));
                $('#sATotalRecharge').html(x(d.total_recharges, true));
                $('#sATotalPackage').html(x(d.total_packs, true));
                $('#sATotalPackageAmount').html(d.total_package_amount);
                $('#sUsers').html(d.unique_users);
                $('#sTotalPrice').html(x(d.total_sells, true));
                $('#sDynamicDiscount').html(x(d.dynamic_discounts, true, true));
            },
            error: function(er){
                post_error(er, null, $(this));
            }
        });
    });
    $('#bServiceData').on('click', function(){
        var t = $('#tServiceData').find('tbody').empty();
        $.ajax({
            url: '/factor/analyse/service/',
            method: 'get',
            data: $('#fSearch').serialize(),
            dataType: 'json',
            success: function(d){
                var $tr = $('<tr>');
                var $tr2 = $('<tr>');
                $tr.append(
                    $('<td>').html(get_price_cell_formatter(d.float_service, true)),
                    $('<td>').html(get_price_cell_formatter(d.normal_service, true)),
                    $('<td>').html(get_price_cell_formatter(d.package, true)),
                    $('<td>').html(get_price_cell_formatter(d.ip, true)),
                    $('<td>').html(d.users)
                );
                $tr2.append(
                    $('<td>').html(d.float_service_count),
                    $('<td>').html(d.normal_service_count),
                    $('<td>').html(d.package_count),
                    $('<td>').html(d.ip_count),
                    $('<td>').html('-')
                );
                t.append($tr, $tr2);
            },
            error: function(er){
                post_error(er, null, null);
            }
        });
    });
});
