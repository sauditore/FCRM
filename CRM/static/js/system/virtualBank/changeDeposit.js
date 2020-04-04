/**
 * Created by saeed on 4/10/16.
 */
$(function(){
    var m = $('#addNewModal');
    m.on('show.bs.modal', function(e){
        var tg = $(e.relatedTarget);
        var invoice = tg.data('pk');
        if(invoice!=undefined && invoice != null){
            m.find('[name=inv]').prop('readonly', true).val(invoice).trigger('change');
        }
        $.ajax({
            url: "/factor/debit/user/j/?u=" + tg.data('cpk'),
            method: 'get',
            dataType: 'json',
            success: function(dt){
                m.find('#mid').val(dt.pk);
                m.find('#mun').val(dt.name);
                m.find('#old').val(dt.debit + " تومان");
                $('#hu').val(dt.pk);
                m.find('#tds').val(dt.subject + ' -- ' + dt.comment);
            },
            error: function(er){
                post_error(er);
            }
        });
        $.ajax({
            url: "/factor/debit/subject/g/",
            method: 'get',
            dataType: 'json',
            success: function(dx){
                var sS =$('#sSubjects');
                sS.empty();
                $.each(dx, function(a, b){
                    var o = new Option(b.pk, b.pk);
                    $(o).html(b.name);
                    sS.append(o);
                });
            },
            error: function(er){
                post_error(er);
            }
        });
    });
    m.find('form').on('submit', function(e){
        e.preventDefault();
        var frm = $(this);
        var data = frm.serialize();
        $.ajax({
            url: frm[0].action,
            data: data,
            method: 'post',
            success: function(){
                m.modal('hide');
                reselectCurrent();
                sAlert('تغییرات با موفقیت انجام شد');
            },
            error: function(x){
                post_error(x,null,m);
            }
        });
    });
});