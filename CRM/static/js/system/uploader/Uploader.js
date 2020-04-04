/**
 * Created by amirp on 2/9/2016.
 */
$(function(){
    $('#mUploader').on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        $(this).find('[name=pk]').val(btn.data('pk'));
    });
});
