/**
 * Created by saeed on 12/5/2015.
 */

$(function(){
    var mv = $('#mViewTransportTypes');
    mv.on('show.bs.modal', function(){
        var tbl = mv.find('table').find('tbody');
        tbl.empty();
        mv.find('.alert').addClass('hidden');
        $.ajax({
            url: '/transport/types/',
            dataType: 'json',
            method: 'get',
            success: function(d){
                $.each(d.data, function(a,b){
                    var tr = $('<tr>');
                    var td0 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    var bDel = $('<button>');
                    var biDel = $('<i>');
                    var bsDel = $('<span>');
                    if(d.has_del_perm){
                        biDel.addClass('glyphicon').addClass('glyphicon-trash');
                        bsDel.addClass('hidden-sm').addClass('hidden-xs').html('حذف');
                        bDel.addClass('btn').addClass('btn-sm').addClass('btn-danger').append(biDel).append(bsDel);
                        bDel.off('click').on('click', function(){
                            $.ajax({
                                url: '/transport/types/rm/?t='+b.ext,
                                method: 'get',
                                success: function(){
                                    bDel.parent().parent().addClass('hidden');
                                },
                                error: function(er){
                                    mv.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                                    setTimeout(function(){
                                        mv.find('.alert').addClass('hidden');
                                    }, 5000);
                                }
                            });
                        });
                    }
                    td0.html(parseInt(a) + 1);
                    td1.html(b.name);
                    td2.append(bDel);
                    tr.append(td0).append(td1).append(td2);
                    tbl.append(tr);
                });
            },
            error: function(er){
                mv.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                setTimeout(function(){
                    mv.find('.alert').addClass('hidden');
                    }, 5000);
            }
        })
    })
});