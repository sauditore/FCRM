/**
 * Created by amirp on 2/11/2016.
 */

$(function(){
    var mh = $('#mUploaded');
    mh.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        $.ajax({
            url: 'upload/view/?pk='+btn.data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(d){
                var t = mh.find('table').find('tbody');
                t.empty();
                $.each(d, function(a, b){
                    var tr= $('<tr>');
                    var td0 = $('<td>');
                    var td4 = $('<td>');
                    var td1 = $('<td>');
                    var td2 = $('<td>');
                    var td3 = $('<td>');
                    td0.html(b.pk);
                    td1.html(b.original_name);
                    td2.html(b.uploader__first_name);
                    td3.html(b.user__first_name);
                    tr.append(td0, td4, td1, td2, td3);
                    t.append(tr);
                });
            },
            error: function(er){
                show_error(er.responseText, mh);
            }
        });
    });
});