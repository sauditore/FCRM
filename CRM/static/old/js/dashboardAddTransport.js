/**
 * Created by saeed on 12/6/2015.
 */

$(function(){
    var mj = $('#mAddJobTransport');
    var fj = $('#fAddJobTransport');
    mj.off().on('show.bs.modal', function(mje){
        var btn = $(mje.relatedTarget);
        var tsp = $('#tJobTransport').find('tbody');
        tsp.empty();
        $.ajax({
            url: '/transport/?current=1&rowCount=-1',
            dataType: 'json',
            method: 'get',
            success: function(d) {
                $.each(d.rows, function(a,b){
                    var tr = $('<tr>');
                    var td0 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    var td3 = $('<td>');
                    var td4 = $('<td>');
                    var bac = $('<button>');
                    var iac = $('<i>');
                    var sac = $('<span>');
                    sac.addClass('hidden-sm').addClass('hidden-xs').html(' انتخاب');
                    iac.addClass('glyphicon').addClass('glyphicon-check');
                    bac.addClass('btn').addClass('btn-info').addClass('btn-sm').append(iac).append(sac).attr('type', 'button');
                    bac.data('pk', b.external);
                    bac.off('click').on('click', function(){
                        mj.find('[type=hidden]').val(bac.data('pk'));
                        fj.submit();
                        var tbl = $('#tDashboard');
                        var xxs = tbl.bootgrid('getSelectedRows');
                        tbl.bootgrid('deselect');
                        tbl.bootgrid('select', xxs);
                    });
                    td4.append(bac);
                    td3.html(b.description);
                    td2.html(b.transport_type__name);
                    td1.html(b.name);
                    td0.html(parseInt(a) + 1);
                    tr.append(td0).append(td1).append(td2).append(td3).append(td4);
                    tsp.append(tr);
                    //var o = $('<option>');
                    //o.val(b.pk).html(b.name);
                    //tsp.append(o);
                })
            },
            error: function(er){
                mj.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                setTimeout(function(){
                    mj.find('.alert').addClass('hidden');
                }, 5000);
            }
        });
        fj.off('submit').on('submit', function(fje){
            fje.preventDefault();
            $.ajax({
                url: '/dashboard/transport/add/?j='+btn.data('pk')+'&'+fj.serialize(),
                //data: ,
                method: 'get',
                success: function(){
                    mj.modal('hide');
                    var tbl = $('#tDashboard');
                    var xxs = tbl.bootgrid('getSelectedRows');
                    tbl.bootgrid('deselect');
                    tbl.bootgrid('select', xxs);
                },
                error: function(er){
                    mj.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                    setTimeout(function(){
                        mj.find('.alert').addClass('hidden');
                    }, 5000);
                }
            })
        })
    });
});
