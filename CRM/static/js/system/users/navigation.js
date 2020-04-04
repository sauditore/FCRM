
$(function(){
    $('#aResetTemp').on('click', function(ae){
        ae.preventDefault();
        $this = $(this);
        $.ajax({
            url: $this.attr('href'),
            method: 'get',
            success: function(){
                document.location.reload();
            },
            error: function (er) {
                post_error(er, null, null);
            }
        })
    });
    $('#mContracts').modal('show');
    $('#fContracts').on('submit', function(fs){
        fs.preventDefault();
        var $this = $(this);
        $.ajax({
            url: $this.attr('action'),
            method: 'get',
            data: $this.serialize(),
            success: function(){
                location.reload();
            },
            error: function(er){
                post_error(er, null);
            }
        })
    });
    $('#bSPass,#bSBN').on('click', function(){
        var $this = $(this);
        sAlert('آیا از ارسال پیام اطمینان دارید؟', 1, function() {
            $.ajax({
                url: $this.data('url'),
                method: 'post',
                data: 'u='+$this.data('pk'),
                success: function () {
                    sAlert('اطلاعات کاربری با موفقیت ارسال شد', 2);
                },
                error: function (er) {
                    post_error(er);
                }
            });
        });
    });
    $('[data-action="dDed"]').on('click', function(){
        var $this = $(this);
        sAlert('آیا از حذف حساب اختصاصی اطمینان دارید؟', 1, function(){
            $.ajax({
                url: $this.data('url'),
                method: 'get',
                data: 'pk='+$this.data('pk'),
                success: function(){
                    sAlert('حساب اختصاصی حذف شد', 2);
                    location.reload();
                }
                ,error: function (er) {
                    post_error(er);
                }
            })
        });
    });
    $('[data-action="dDC"]').on('click', function(){
        var $this = $(this);
        sAlert('آیا از حذف اطلاعات حقوقی اطمینان دارید؟', 1, function(){
            $.ajax({
                url: $this.data('url'),
                method: 'get',
                data: 'pk='+$this.data('pk'),
                success: function(){
                    sAlert('حساب حقوقی حذف شد', 2);
                    location.reload();
                }
                ,error: function (er) {
                    post_error(er);
                }
            })
        });
    });
});
