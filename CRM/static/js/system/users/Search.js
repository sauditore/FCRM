/**
 * Created by saeed on 4/5/16.
 */

$(function(){
    $('#ii').on('input', function(){
        if($(this).val().length==5){
            $('#frmSearch').submit();
        }
    }).focus();
    $('#frmSearch').on('submit', function(fs){
        fs.preventDefault();
        var that = $(this);
        $('#fSdx').val(that.serialize());
        reloadCurrent();
        document.location = '#srx';
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'active': function(c,r){
                var i = $('<i>').addClass('fa');
                if(r.is_active){
                    i.addClass('fa-check text-info');
                }else{
                    i.addClass('fa-remove text-danger')
                }
                return $('<div>').append(i).html()

            },
            'nav': function(c,r){
                var text = r.pk;
                if(c.id=='fk_ibs_user_info_user__ibs_uid'){
                    text = r.fk_ibs_user_info_user__ibs_uid;
                }
                return $('<div>').append($('<a>').attr({'href':'/user/nav/?uid='+ r.pk, 'target': '_blank'}).html(text)).html()
            }
        },
        ajax: true,
        url_prefix: "/user/search/",
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
        var s = r[0];
        summery.append($('<hr>'));
        var holder = $('<div>').addClass('row');
        summery.append(holder);
        var user_type = $('<div>').addClass('col-md-3').append('نوع کاربر : ');
        holder.append(user_type);
        var user_service = $('<div>').addClass('col-md-3').append('سرویس : ');
        //var service_expire = $('<div>').addClass('col-md-3').append('تاریخ انقضا : ');
        var user_address = $('<div>').addClass('col-md-3').append('آدرس : ');
        holder.append(user_address);
        user_address.append(s.fk_user_profile_user__address);
        var user_email = $('<div>').addClass('col-md-3').append('ایمیل : ').append(s.email);
        holder.append(user_email);
        if(s.is_staff && s.is_superuser){
            user_type.append('مدیریت');
        }else if(s.is_staff){
            user_type.append('پرسنل');
        }else{
            user_type.append('مشتری');
            if(s.fk_user_profile_user__is_dedicated){
                user_type.append(' - اختصاصی');
            }
            if(s.fk_user_profile_user__is_company){
                user_type.append(' - حقوقی');
            }
            var srv = s.fk_user_current_service_user__service__name;
            var exp = s.fk_user_current_service_user__expire_date;
            if(!srv){
                srv = 'فاقد سرویس';
            }
            if(!exp){
                exp = 'بدون تاریخ!'
            }
            holder.append(user_service.append(srv, ' - تاریخ انقضا :‌' + exp));
        }
        var actions = $('<div>').addClass('row text-center').append(
            $('<a>').addClass('btn btn-sm btn-primary').append('پنل کاربری').attr({'href': '/user/nav/?uid='+ s.pk, 'target': '_blank'})
        );
        summery.append($('<hr>'), actions);

    }).on('loaded.grid', function(){
        var cr = $(this).bootgrid('getCurrentRows');
        if(cr.length == 1){
            setTimeout(function(){
                document.location = '/user/nav/?uid='+cr[0].pk;
            }, 500);

        }
    });
});
