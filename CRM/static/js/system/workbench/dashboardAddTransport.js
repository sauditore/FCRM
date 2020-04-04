/**
 * Created by saeed on 12/6/2015.
 */

$(function(){
    var mj = $('#mAddJobTransport');
    var fj = $('#fAddJobTransport');
    mj.off().on('show.bs.modal', function(mje){
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
                    bac.addClass('btn btn-info btn-sm').append(iac).append(sac).attr('type', 'button');
                    bac.off('click').on('click', function(){
                        mj.find('[name=t]').val(b.external);
                        mj.find('#slx').val(td1.html());
                        fj.submit();
                    });
                    td4.append(bac);
                    td3.html(b.description);
                    td2.html(b.transport_type__name);
                    td1.html(b.name);
                    td0.html(parseInt(a) + 1);
                    tr.append(td0).append(td1).append(td2).append(td3).append(td4);
                    tsp.append(tr);
                })
            },
            error: function(er){
                show_error(er.responseText);
            }
        });
        fj.off('submit').on('submit', function(fje){
            fje.preventDefault();
            sAlert('آیا از انتخاب '+fj.find('#slx').val()+' اطمینان دارید؟', 1, function(){
                $.ajax({
                    url: '/dashboard/transport/add/?',
                    data: fj.serialize(),
                    method: 'get',
                    success: function(){
                        mj.modal('hide');
                        reselectCurrent();
                        sAlert(fj.find('#slx').val()+' برای حمل و نقل انتخاب شد', 2);
                    },
                    error: function(er){
                        show_error(er.responseText);
                    }
                })
            });
        })
    });
});
