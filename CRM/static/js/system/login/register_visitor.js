$(function(){
    $('#fVisitor').on('submit', function(fs){
        fs.preventDefault();
        var $this = $(this);
        $.ajax({
            url: $this.attr('action'),
            method: 'post',
            data: $this.serialize(),
            success: function(){
                sAlert('ثبت نام انجام شد', 2);
                document.location = '/public/reseller/';
            },
            error: function(er){
                post_error(er, null);
            }
        })
    })
});
