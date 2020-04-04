/**
 * Created by saeed on 4/28/16.
 */
$(function(){
    $('#dvSelectUserTower').on('show.bs.modal', function(e){
        var t = $(e.relatedTarget);
        var u = t.data('pk');
        var m = $(this);
        var fx = $('#fAssignUserTower');
        fx.off('submit');
        $.ajax({
            url: "/tower/gut/" + '?u=' + u,
            method: 'get',
            dataType: "json",
            success: function(d){
                var tw = $('#sTowers');
                tw.empty();
                $.each(d.towers, function (a, b){
                    var o = new Option(b[0], b[0]);
                    if(b[0] == d.selected){
                        $(o).html(b[1]).attr('selected', 'selected');
                    }
                    else{
                        $(o).html(b[1]);
                    }
                    tw.append(o);
                });
                tw.off('change');
                tw.on('change', function(x1){
                    $.ajax({
                        url: "/tower/des/?t="+$(x1.target).val(),
                        method: 'get',
                        success: function(d){
                            $('#dvDes').removeClass('hidden').html(d);
                        },
                        error: function(er){
                            post_error(er, null, m);
                        }
                    });
                });
                tw.select2({dir: 'rtl'});
            },
            error: function(er){
                post_error(er, null, m);
            }
        });
        fx.on('submit', function (s){
            s.preventDefault();
            var f = $(s.target);
            $.ajax({
                url: f.attr('action') + '?' + f.serialize(),
                success: function(){
                    m.modal('hide');
                    sAlert('تغییرات با موفقیت انجام شد', 2);
                    location.reload();
                },
                error: function(er){
                    post_error(er, null, m);
                }
            });
        });
        m.find('input[type=hidden]').val(u);
    });

});
