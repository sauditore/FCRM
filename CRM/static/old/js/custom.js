
function assign(){
    do_request('/user/assign/', '#frmAssign', 'spMessage', function(){document.location='/user/show/all/'});
}
function create_perm_load(){
    $(document).ready(function(){
        var ptid = document.getElementById('pt_id');
    if(ptid!=null){
        get_request('/perm/show/types/?pid='+ptid.value, 'dvPermTypes', 'spMessage');
    }
    else{
        get_request('/perm/show/types/', 'dvPermTypes', 'spMessage');
    }
    });

}
function create_perm(){
    do_request('/perm/create/', '#frmPerms', 'spMessage', function(){document.location='/perm/show/all/'});
}

function create_permission_type(){
    do_request('/perm/create/types/', '#frmPermTypes', 'spMessage', function(){document.location="/perm/show/all/types/"});
}
function get_request2(url,suc,er){
    $.ajax({
        type: 'GET',
        url: url,
        success: function(data){document.getElementById(suc).value=data},
        error: function(data){document.getElementById(er).value=data.responseText}
    });
}
function refresh_data(){
        get_request('/ajax/?a=sts&t=d', 'hDashboard', 'hDashboard');
        get_request('/ajax/?a=sts&t=ord', 'hOrders', 'hOrders');
        get_request('/ajax/?a=sts&t=o', 'spo', 'spo');
        get_request('/ajax/?a=sts&t=t', 'spt', 'spt');
        get_request('/ajax/?a=sts&t=f', 'spf', 'spf');
        get_request('/ajax/?a=ou', 'sco', 'sco');
        setTimeout(refresh_data, 5000);
}
function loader(e){
    get_request(e.currentTarget.href, 'content_wrap', 'content_wrap');
//    alert(e.currentTarget.href);
    e.preventDefault();
}