$(function () {
    var packs = $('#tPackages');
    var fa = $('#fAddPricePack');
    fa.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            method: 'post',
            url: '/factor/debit/package/add/',
            data: fa.serialize(),
            success: function() {
                packs.bootgrid('reload');
                fa.find('input').val('');
            },
            error: function(er){
                show_error(er.responseText);
            }
        });
    });

    packs.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {},
        ajax: true,
        url: function () {
            return "/factor/debit/package/";
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
        $('[name=p]').val(r[0].ext);
        fg.removeClass('hidden');
        $.ajax({
            url: '/factor/debit/package/groups/?pk='+r[0].ext,
            method: 'get',
            dataType: 'json',
            success: function(d){
                $('#dGroups').find('input').each(function(){
                    if($.inArray(parseInt($(this).attr('id')), d) > -1){
                        $(this).prop('checked', true);
                    }
                    else{
                        $(this).prop('checked', false);
                    }
                })
            },
            error: function(er){
                show_error(er.responseText);
            }
        });
    });
    var fg = $('#fAddPackageGroups');
        fg.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/factor/debit/package/groups/add/',
                method: 'post',
                data: fg.serialize(),
                success: function(){
                    sAlert('گروه ها با موفقیت ویرایش شد', 2);
                },
                error: function(er){
                    show_error(er.responseText);
                }
            })
    });
});