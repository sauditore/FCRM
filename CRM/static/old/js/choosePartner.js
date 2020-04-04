/**
 * Created by saeed on 12/1/2015.
 */
$(function(){
    var m = $('#mChoosePartner').on('show.bs.modal', function(ms){
        var t = m.find('table').find('tbody');
        var dpk = $(ms.relatedTarget).data('pk');
        t.empty();
        $.ajax({
            method: 'get',
            url: "/dashboard/partner/?d="+dpk,
            dataType: 'json',
            success: function(d){
                $.each(d.users, function(a, b){
                    var r = $('<tr>');
                    var td0 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    td0.html(b[0]);
                    td1.html(b[1]);
                    var adb = $('<button>');
                    var is_selected = $.inArray(b[0], d.active) >= 0;
                    adb.on('click', function(){
                        var xc = 1;
                        var _this = $(this);
                        if(_this.data('active')=='1'){
                            xc = 2;
                        }
                        var dxd = 't='+b[0]+'&d='+dpk+'&c='+xc;
                        $.ajax({
                            method: 'post',
                            data: dxd,
                            url: '/dashboard/partner/add/',
                            success: function(){
                                if(xc==1){
                                    _this.data('active', '1');
                                    _this.removeClass('btn-info').addClass('btn-danger').find('i').removeClass('glyphicon-plus').addClass('glyphicon-remove');
                                }
                                else{
                                    _this.removeClass('btn-danger').addClass('btn-info').data('active', '').find('i').addClass('glyphicon-plus').removeClass('glyphicon-remove');
                                }
                            },
                            error: function(er){
                                m.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                                setTimeout(function(){
                                    m.find('.alert').addClass('hidden');
                                }, 5000)
                            }
                        });
                    });
                    var idb = $('<i>');
                    idb.addClass('glyphicon');
                    adb.addClass('btn').addClass('btn-sm').append(idb);
                    if(is_selected) {
                        idb.addClass('glyphicon-remove');
                        adb.addClass('btn-danger');
                        adb.data('active', '1');
                    }
                    else {
                        idb.addClass('glyphicon-plus');
                        adb.addClass('btn-info');
                    }
                    td2.append(adb);
                    r.append(td0).append(td1).append(td2);
                    t.append(r);
                });
            },
            error: function(er){
                m.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                setTimeout(function(){
                    m.find('.alert').addClass('hidden');
                }, 5000);
            }
        });
    })
});