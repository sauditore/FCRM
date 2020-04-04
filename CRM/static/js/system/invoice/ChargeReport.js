/**
 * Created by saeed on 6/12/16.
 */

$(function(){
    var $m = $('#mCharged');
    var t = $m.find('table>tbody');
    $m.on('show.bs.modal', function(e){
        var $b = $(e.relatedTarget);
        t.empty();
        $.ajax({
            url: '/factor/charges/?pk='+$b.data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d, function(a,b){
                    var $tr = $('<tr>');
                    var $td0 = $('<td>').html(b.last_update);
                    if(b.success){
                        $td0.addClass('data-accepted');
                    }
                    else{
                        $td0.addClass('data-rejected');
                    }
                    $tr.append(
                        $td0,
                        $('<td>').html(b.failed_action)
                    );
                    t.append($tr);
                });

            },
            error: function(er){
                post_error(er, null, $m);
            }
        });
    })
});
