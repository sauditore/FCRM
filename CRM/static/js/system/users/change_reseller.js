/**
 * Created by saeed on 5/18/16.
 */
$(function(){
    $.ajax({
        url: "/user/reseller/json/",
        dataType: 'json',
        success: function(d){
            var s = $('#sReseller');
            var s2 = $('#sVis');
            $.each(d, function(a, b){
                var x = $('<option>');
                x.html(b.first_name);
                x.val(b.pk);
                if(b.is_reseller){
                    s.append(x);
                }
                else if(b.is_visitor){
                    s2.append(x);
                }
            });
        },
        error: function(er){
            post_error(er, null, null)
        }
    });
    $('#dvChangeOwner').on('show.bs.modal', function(e){
        var m = $(this);
        var bx = $(e.relatedTarget);
        m.find('[name=u]').val(bx.data('pk'));
    });
    $('#bChangeOwner').on('click', function(x){
        x.preventDefault();
        $.ajax({
            url: "/user/reseller/chw/?",
            method: 'get',
            data: $('#fChangeOwner').serialize(),
            success: function(){
                $('#dvChangeOwner').modal('hide');
                sAlert('نماینده با موفقیت تغییر یافت', 2);
            },
            error: function(er){
                post_error(er, null, null)
            }
        });
    });
});
