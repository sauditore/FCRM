/**
 * Created by saeed on 5/16/16.
 */
$(function(){
    $("#b").persianDatepicker();
    $('#mrd').persianDatepicker();
    $('form[method=post]').on('submit', function(fs){
        fs.preventDefault();
        var $this = $(this);
        $.ajax({
            url: $this.attr('action'),
            method: 'post',
            data: $this.serialize(),
            success: function(){
                sAlert('تغییرات با موفقیت انجام شد',2);
            },
            error: function(er){
                post_error(er, null, $this);
            }
        })
    });
    $('[type=radio][data-actor="1"]').on('change', function(){
        var $this = $(this);
        if($this.is(':checked')){    // if related check then remove hidden class for related groups
            $('[data-group]').addClass('hidden');
            //$('[data-related]').prop('disabled', true);
            $('[data-group=#'+$this.attr('id')+']').removeClass('hidden');
            $('[data-related=#'+$this.attr('id')+']').prop('disabled', false);
        }
        else{   // else $this is not checked! so add hidden class for related groups
            $('[data-group=#'+$this.attr('id')+']').addClass('hidden');
            $('[data-related=#'+$this.attr('id')+']').prop('disabled', true);
        }
    });
});
