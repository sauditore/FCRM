/**
 * Created by saeed on 4/28/16.
 */

$(function(){
    var times=0;
    $('#mIEdit').on('show.bs.modal',function(me){
        var btn = $(me.relatedTarget);
        var $this = $(this);
        clear_on_open($this);
        if(btn.length){
            $.ajax({
                url: '/factor/comment/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    $this.find('[name=pk]').val(d.pk);
                    $this.find('[name=b]').val(d.ref_number);
                    $this.find('[name=d]').val(d.comment);
                },
                error: function(er){
                    post_error(er, null, $this);
                }
            });
        }
    });
    $('#fIEdit').on('submit', function(fs){
        fs.preventDefault();
        var $this = $(this);
        $.ajax({
            method: 'post',
            url: $this.data('action'),
            data: $this.serialize(),
            success: function(){
                $('#mIEdit').modal('hide');
                sAlert('تغییرات بت موفقیت انجام شد',2);
            },
            error: function(er){
                post_error(er, null, $this);
            }
        });
    });
});
