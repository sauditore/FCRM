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
                var uploaded = $('#tFileHolder').find('tbody');
                uploaded.empty();
                $.each(d, function(a, b){
                    var tr = $('<tr>');
                    var pk = $('<td>');
                    //var ofn = $('<td>');
                    var dt = $('<td>');
                    var uploader = $('<td>');
                    var owner = $('<td>');
                    var prv = $('<td>');
                    var  imx = $('<img>');
                    pk.html(b.pk);
                    dt.append($('<a>').attr('href','/user/download/?pk='+ b.ext).attr('target', '_blank').html(b.upload_date));
                    uploader.html(b.uploader__first_name);
                    owner.html(b.user__first_name);
                    imx.addClass('img-responsive').attr('src','/static/thumb/'+ b.ext+'_'+ b.original_name+'.jpg').on('error', function(){
                        $(this).parent().removeClass('image').addClass('icon').append($('<i>').addClass('fa fa-file'));
                        $(this).remove();
                    });
                    prv.addClass('image').append(imx);
                    tr.append(pk, dt,
                        uploader, owner, prv);
                    uploaded.append(tr);
                });
            },
            error: function(er){
                post_error(er);
            }
        });
    });
});