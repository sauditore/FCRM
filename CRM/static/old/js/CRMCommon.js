
$(function(){
    bindSelect2();
    bindMaxLen();
    var loc = window.location.pathname;
    var ax = $('nav').not('#nTopNav').find('a[href="'+loc+'"]');
    ax.parents().not('body,html,#side-menu,nav,div').each(function(){
        var _this = $(this);
        if(_this.prop('tagName') == 'LI'){

            _this.addClass('active').find('ul').not('.nav-third-level').addClass('in');
        }
        else if(_this.prop('tagName') == 'UL'){
            if(_this.hasClass('nav-third-level')){
                _this.addClass('in');
            }
        }
    });
    loadFloatable();
    bindSearch();
    //setTimeout(function(){
        document.location = '#body';
    //}, 10);
    if($('[data-dashboard-counter="1"]').length){
        setTimeout(function(){
            $.ajax({
                url: '/ajax/?t=d&a=sts',
                method: 'get',
                success: function(d){
                    $('[data-dashboard-counter="1"]').html(d);
                }
            });
        }, 1500);
    }
});
function bindSelect2 (holder){
    try{
        if(holder == undefined) {
            $('select[data-select=1]').css('width', '100%').select2({
                dir: "rtl",
                tags: true
            })
        }
        else {
            holder.find('select[data-select=1]').css('width', '100%').select2({
                dir: "rtl",
                tags: true
            });
        }
    }
    catch(e){
        console.log(e);
    }

}
function bindMaxLen(holder){
    try{
        if(holder==undefined) {
            $('input[maxlength]').maxlength({
                threshold: 2000
            });
        }
        else {
            holder.find('input[maxlength]').maxlength({
                threshold: 2000
            });
        }
    }
    catch (e){
        console.log(e);
    }
}
function buildMailSummery(data){
    var li = $('<li>');
    li.append(
        $('<div>').append(
            $('<a>').append(
                $('<img>').addClass('img-circle').attr('src', data.profile_image || '/static/img/no-image.png')
            ).addClass('pull-left').attr('href', '#'),
            $('<div>').append(
                $('<small>').html(data.mail_date).addClass('pull-right'),
                $('<strong>').html(data.subject),
                $('<br>'),
                $('<small>').text(data.sender).addClass('text-muted')
            )
        ).addClass('dropdown-messages-box')
    );
    return li;
}
function loadMailSummery(){
    $.ajax({
        url: '/mail/',
        method: 'get',
        dataType: 'json',
        success: function(data){
            $.each(data.rows, function(a,b){
                var res = buildMailSummery(b);
                //console.log(res)
                $('#mail_box_summery').prepend(res, $('<li>').addClass('divider'));
            })
        },
        error: function(er){

        }
    });
}
function init_toast(){
    toastr.options = {
          "closeButton": true,
          "debug": false,
          "progressBar": true,
          "preventDuplicates": false,
          "positionClass": "toast-top-center",
          "onclick": null,
          "showDuration": "400",
          "hideDuration": "1000",
          "timeOut": "7000",
          "extendedTimeOut": "2000",
          "showEasing": "swing",
          "hideEasing": "linear",
          "showMethod": "fadeIn",
          "hideMethod": "fadeOut"
    };
    return toastr;
}
function show_error(msg){
    init_toast()['error'](msg, 'خطا');
}
function reload_grid(holder){
    holder.bootgrid('reload');
}
function reselect_grid(holder){
    var s = holder.bootgrid('getSelectedRows');
    holder.bootgrid('deselect');
    holder.bootgrid('select', s);
}
function rebindModal(holder){
    holder.find('[data-toggle=modal]').on('click', function(){
        $($(this).data('target')).modal('show', this);
    })
}
function post_error(msg, param, holder){
    var m = '';
    var p = undefined;
    var h = $('body');
    var jn = false;
    if(msg.responseJSON!=undefined){
        m = msg.responseJSON.msg;
        jn = true;
    }
    else if(msg.reponseText!=undefined){
        m = msg.responseText;
    }
    else{
        m = msg;
    }
    if(jn){
        p = msg.responseJSON.param;
    }
    else{
        p = param;
    }
    if(holder!=undefined && holder != null){
        if(holder.length){
            h = holder;
        }
    }
    else{
        holder=$('body');
    }
    show_error(m);
    if(p!=undefined && p!=null){
        var x = h.find('[name='+p+']');
        x.parents().find('div.collapse').has(x).collapse('show');
        if(x.hasClass('select2-hidden-accessible')){
            x = x.next().find('.select2-selection--single');
        }
        x.focus();
        x.addClass('elem-focus');
        setTimeout(function(){
            holder.find('[name='+p+']').removeClass('elem-focus');
        }, 1500)
    }
}
function clear_on_open(holder){
    holder.find('input[type=text]').val('').trigger('change');
    holder.find('textarea').val('').trigger('change');
    holder.find('[type=hidden][name=pk]').val('');
}
function post_ok(msg){
    init_toast()['success'](msg, 'تایید عملیات');
}
function light_loading(holder){
    holder.addClass('loading')
}
function light_loaded(holder){
    holder.removeClass('loading')
}
function translate_bool(b){
    var i = $('<i>');
    i.addClass('glyphicon');
    var s = $('<span>');
    if(b==true){
        i.addClass('glyphicon-check');
        s.addClass('text-success');
    }
    else{
        //return 'خیر'
        i.addClass('glyphicon-remove');
        s.addClass('text-default');
    }
    s.append(i);
    return $('<span>').append(s).html();
}
function load_problems(){
    get_request('/ajax/?a=prb', 'slProblem', 'slProblem');
}
function load_solution() {
    var question = document.getElementById('slProblem').value;
    get_request('/ajax/?a=sln&q=' + question, 'slSolution', 'slSolution');
    load_description_for(0);
}
function load_description_for(dv){
    if(dv==0){
        get_request('/ajax/?a=lpd&q='+document.getElementById('slProblem').value, 'dvPDescription', 'dvDescription');
    }
    else{
        get_request('/ajax/?a=lsd&s='+document.getElementById('slSolution').value, 'dvSDescription', 'dvDescription');
    }
}
function do_request(page, frm, err, suc){
    $.ajax({
        type: 'POST',
        url: page,
        data: $(frm).serialize(),
        error: function(data){
            document.getElementById(err).innerHTML = data.responseText
        },
        success: suc
    });
}
function get_date_array(d){
    if(d==null){
        return null;
    }
    var da = d.split('-');
    var day = 0;
    if(da.length==3){
        day = da[2].split(' ')[0];
        da[2] = day;
    }
    if(da.length<2){
        return null;
    }
    return da;
}
function get_date_distance(s, e){
    var tmp0 = get_date_array(s);
    var tmp1 = get_date_array(e);
    var d1 = new Date();
    if(tmp0==null){
        return 0;
    }
    if(tmp1!=null){
        var de = Date.PersianToGregorian('13'+tmp1[0], tmp1[1], tmp1[2]);
        d1 = new Date(de[0], de[1]-1, de[2]);
    }
    var d = Date.PersianToGregorian('13'+tmp0[0], tmp0[1], tmp0[2]);
    var d0 = new Date(d[0], d[1]-1, d[2]);
    return parseInt(Math.abs(d1-d0)/(3600000*24));
}
function get_request(url,suc,er){
    $.ajax({
        type: 'GET',
        url: url,
        success: function(data){document.getElementById(suc).innerHTML=data},
        error: function(data){document.getElementById(er).innerHTML=data.responseText}
    });
}
function loadFloatable(){
    try{
        $('input[placeholder]').floatlabel({
            labelClass: 'form-group-float-persian'
        });
    }
    catch (e){
        console.log(e);
    }
}
function sAlert(msg, t, y, n){
    var sOptions = {
        text: msg
        //: "Yes, delete it!",
    };
    if(t==1){ // Warning
        sOptions['title'] = 'تایید عملیات';
        sOptions['type'] = 'warning';
        sOptions['cancelButtonText'] = 'انصراف';
        sOptions['confirmButtonColor'] = '#DD6B55';
        sOptions['showCancelButton'] = true;
        sOptions['confirmButtonText'] = 'ادامه';
    }
    else if(t==3){
        sOptions['title'] = 'تایید حذف';
        sOptions['type'] = 'error';
        sOptions['cancelButtonText'] = 'انصراف';
        sOptions['confirmButtonColor'] = '#DD6B55';
        sOptions['showCancelButton'] = true;
        sOptions['confirmButtonText'] = 'حذف';
        sOptions['text'] = 'آیا از حذف'+' '+msg+' اطمینان دارید؟';
    }
    else if(t==4){
        sOptions['title'] = 'ورود اطلاعات';
        sOptions['type'] = 'input';
        sOptions['showCancelButton'] = true;
        sOptions['showConfirmButton'] = true;
        sOptions['cancelButtonText'] = 'انصراف';
        sOptions['confirmButtonText'] = 'تایید';
        sOptions['closeOnConfirm'] = false;
        sOptions['text'] = msg;
    }else if(t==5){
        sOptions['title'] = 'خطا';
        sOptions['type'] = 'error';
        sOptions['showCancelButton'] = false;
        sOptions['showConfirmButton'] = false;
        if(y==undefined)
            sOptions['timer'] = 3500;
        else {
            sOptions['confirmButtonText'] = 'تایید';
            sOptions['showConfirmButton'] = true;
        }
    }
    else{
        sOptions['title'] = 'انجام شد';
        sOptions['type'] = 'success';
        sOptions['showCancelButton'] = false;
        sOptions['showConfirmButton'] = false;
        if(y==undefined)
            sOptions['timer'] = 1500;
        else {
            sOptions['confirmButtonText'] = 'تایید';
            sOptions['showConfirmButton'] = true;
        }
    }
    sOptions['closeOnConfirm'] = y == undefined;
    sOptions['closeOnCancel'] = n == undefined;
    //console.log(sOptions);
    swal(sOptions, function(isConfirm){
        if (isConfirm && y!=undefined) {y(isConfirm);} else if(n!=undefined) {n(isConfirm);}else{swal.close();}
    });
}
function bindSearch(){
    var frm = $('#dSearch').find('form');
    frm.on('submit', function(fs){
        fs.preventDefault();
        var _this = $(this);
        $('#fSdx').val(_this.serialize());
        var cur = getCurrentGrid();
        if(cur===null){
            return;
        }
        reloadCurrent();
        document.location = '#body';
    });
}

function getActionArea(){
    return $('<div>').addClass('text-center').append($('#dACTS').clone().css('display', 'block')).clone();
}
function bindDelete(holder){
    holder.find('[data-action="del"]').on('click', function(){
        var that = $(this);
        sAlert('',3, function(){
            $.ajax({
                url: that.data('url')+'?pk='+that.data('pk'),
                method: 'get',
                success: function(){
                    if(getCurrentGrid())
                        reloadCurrent();
                    sAlert('آیتم مورد نظر با موفقیت حذف شد',2);
                },
                error: function(er){
                    post_error(er,null,$('body'))
                }
            })
        })
    });
}
function formatPrice(holder){
    holder.find('.price').priceFormat({
        thousandsSeparator: ',',
        suffix: '',
        clearPrefix: true,
        centsLimit: 0
    });
}
function get_price_cell_formatter(price, as_html, add_color){
    var x = $('<span>').append($('<span>').append(price).addClass('price')).append(' تومان');
    var p = parseInt(price || 0);
    if(p==0){
        return '0'
    }
    if(add_color == true){
        if(p<0){
            x.addClass('text-danger');
        }
        else{
            x.addClass('text-success');
        }
    }
    formatPrice(x);
    if(as_html == true) {
        return $('<div>').append(x).clone().html();
    }
    return x;
}