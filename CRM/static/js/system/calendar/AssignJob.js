/**
 * Created by saeed on 5/2/16.
 */
$(function (){
    var m = $('#mAssignJob');
    var slc = m.find('#sEventT');
    $.ajax({
        url: "/cal/working/types/j/",
        dataType: 'json',
        success: function(xs){
            slc.append($('<option>').prop({'disabled': 'disabled', 'selected': 'selected'}).html('نوع زمانبندی'));
            $.each(xs, function(q, w){
                var o = $('<option>');
                o.attr('value', w.ext).html(w.name);
                slc.append(o);
            });
        }
    });
    m.on('hide.bs.modal', function(){
        m.find('[name=j]').val('');
    }).on('show.bs.modal', function(){
        m.find('table').find('tbody').empty();
    });
    slc.on('change', function(){
        var tbl = m.find('table').find('tbody');
        var has_action = m.find('[name=j]').val() != '';
        $.ajax({
            url: "/cal/working/free/?pk="+slc.val(),
            method: 'get',
            dataType: 'json',
            success: function(d){
                tbl.empty();
                $.each(d, function(a,b){
                    $.each(b.times, function(n,m){
                        var btn = null;
                        if(has_action) {
                            btn = $('<button></button>');
                            btn.attr('data-pk', m.pk.toString()).attr('data-date', b.date);
                            btn.addClass('btn').addClass('btn-xs').addClass('btn-info').attr('type', 'button');
                            btn.on('click', function () {
                                $('#time').val(btn.data('pk'));
                                $('#date').val(btn.data('date'));
                                sAlert('آیا از انتخاب ' + btn.data('text') + ' اطمینان دارید؟', 1, function () {
                                    $.ajax({
                                        url: "/cal/working/rsv/?" + $('#mAssignJob').find('form').serialize(),
                                        method: 'get',
                                        success: function () {
                                            $('#mAssignJob').modal('hide');
                                            reselectCurrent();
                                            sAlert(btn.data('text') + ' با موفقیت ثبت شد', 2);
                                        },
                                        error: function (er) {
                                            post_error(er);
                                        }
                                    });
                                })
                            });
                            var ib = $('<i></i>');
                            ib.addClass('fa').addClass('fa-check');
                            var txt = $('<span></span>');
                            txt.addClass('hidden-xs').addClass('hidden-sm').html(" رزرو");
                            btn.append(ib).append(txt).data('text', 'تاریخ ' + b.date + ' از ساعت ' + m.start_time + ' تا ' + m.end_time);
                        }
                        else{
                            btn = $('<i>').addClass('fa fa-circle-thin');
                        }
                        var tr = $('<tr></tr>');
                        var td0 = $('<td></td>');
                        var td1 = $('<td></td>');
                        var td2 = $('<td></td>');
                        var td3 = $('<td></td>');
                        td0.html(m.name);
                        td1.html(m.start_time+'-'+m.end_time);
                        td2.html(b.date);
                        td3.append(btn);
                        tr.append(td0).append(td1).append(td2).append(td3);
                        tbl.append(tr);
                    });

                });
            },
            error: function(er){
                post_error(er, null, m);
            }
        });
    });
});