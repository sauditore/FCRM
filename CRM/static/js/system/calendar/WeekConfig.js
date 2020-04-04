/**
 * Created by saeed on 5/2/16.
 */
$(function(){
    var frm = $('#fWeekConfig');
    $('#mWeekConfig').on('show.bs.modal', function(me){
        var t = $(this);
        var wd = $(me.relatedTarget).parent();
        t.find('[name=m]').val(wd.data('day'));
        frm.off('submit');
        reload_date();
        frm.on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: frm.attr('action'),
                method: 'post',
                data: frm.serialize(),
                success: function(){
                    reload_date();
                },
                error: function(er){
                    post_error(er);
                }
            });
        });
        function load_events(){
            var dls = $('[data-delete=1]');
            dls.off('click');
            dls.on('click', function(dc){
                var dpk = $(this).data('pk');
                sAlert('آیا از حذف زمان کار اطمینان دارید؟', 1, function(){
                    $.ajax({
                        url: "/cal/working/rm/?w="+dpk,
                        method: 'get',
                        success: function(){
                            reload_date();
                            sAlert('زمان کار با موفقیت حذف شد', 2);
                        },
                        error: function (er){
                            post_error(er);
                        }
                    });
                });
            });
        }
        function reload_date(){
            t.find('input[type=text]').val('');
            $.ajax({
                method: 'get',
                url: "/cal/working/?w="+wd.data('day'),
                dataType: 'json',
                success: function(d){
                    var table = t.find('table');
                    table.find('tbody').empty();
                    $.each(d, function(a,z){
                        var tr = $('<tr></tr>');
                        var td0 = $('<td></td>');
                        var td1 = $('<td></td>');
                        var td2 = $('<td></td>');
                        var td3 = $('<td></td>');
                        var td4 = $('<td></td>');
                        var db = $('<button></button>');
                        var dbs = $('<span></span>');
                        var dbi = $('<i></i>');
                        dbs.addClass('hidden-xs').addClass('hidden-sm').html("حذف");
                        db.addClass('btn').addClass('btn-xs').attr('type', 'button').addClass('btn-danger').attr('data-pk', z.pk).attr('data-delete', '1').append(dbi).append(dbs);
                        dbi.addClass('glyphicon');
                        dbi.addClass('glyphicon-trash');

                        td0.html(z.event_type__name);
                        td1.html(z.name);
                        td2.html("از " + z.start_time + "  تا  " + z.end_time);
                        td3.html(z.resource);
                        td4.append(db);
                        tr.append(td0);
                        tr.append(td1);
                        tr.append(td2);
                        tr.append(td3);
                        tr.append(td4);
                        table.find('tbody').append(tr);
                    });
                    load_events();
                },
                error: function(er){
                    t.find('.alert').removeClass('hidden').find('span').html(er.responseText);
                }
            });
        }

    });
});