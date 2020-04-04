/**
 * Created by saeed on 3/13/16.
 */
$(function(){
    var cu = $('[name=current]');
    var inbox = $('#tInbox');
    $('[data-act]').on('click', function(){
        var data = '';
        inbox.find('[type=checkbox] :checked').each(function(a,b){
            data += 'cbm='+$(b).val();
        });
        if($(this).data('act') == '1') {
            $.ajax({
                url: '/mail/read/',
                method: 'post',
                data: data,
                success: function () {
                    init_data()
                },
                error: function (er) {
                    post_error(er.responseJSON.msg);
                }
            });
        }
    });
    $(function(){
        setInterval(function(){
            $.ajax({
                url: '/mail/refresh/',
                method: 'get',
                success: function(d){
                    $('#spMail').html(d)
                }
            });
        }, 10000);
    });
    $('[data-refresh]').on('click', function(){
        $.ajax({
            url: '/mail/refresh/',
            method: 'get',
            success: function(){
                cu.val('1');
                $('.pagination').pagination('selectPage', 1);
            },
            error: function(er){
                post_error(er.responseJSON.msg);
            }
        })
    });
    $('.pagination').pagination({
        itemsOnPage: 10,
        prevText: 'قبلی',
        nextText: 'بعدی',
        onPageClick: function(p,e){
            $('[name=current]').val(p);
            init_data();
            e.preventDefault();
        }
    });
    $('[data-next]').on('click', function(ae){
        ae.preventDefault();
        cu.val(parseInt(cu.val())+1);
        init_data();
    });
    $('[data-back]').on('click', function(ae){
        ae.preventDefault();
        cu.val(parseInt(cu.val()) - 1);
        init_data();
    });
    $('[data-select]').on('click', function(){
        var _this = $(this);
        var tp = _this.data('select');
        if(tp=='0'){
            inbox.find('[type=checkbox]').prop('checked', false);
        }
        else if(tp=='3'){
            if(_this.prop('checked')){
                inbox.find('[type=checkbox]').prop('checked', true);
            }
            else{
                inbox.find('[type=checkbox]').prop('checked', false);
            }
        }
        else if(tp=='1'){
            inbox.find('[data-read="true"]').prop('checked', true);
            inbox.find('[data-read="false"]').prop('checked', false);
        }
        else if(tp=='2'){
            inbox.find('[data-read="false"]').prop('checked', true);
            inbox.find('[data-read="true"]').prop('checked', false);
        }
    });
    function init_data(){
        $.ajax({
            url: '/mail/?',
            method: 'get',
            dataType: 'json',
            data: $('#fPager').serialize(),
            success: function(d){
                $('.pagination').pagination('updateItems', d.total);
                var tbo = inbox.find('tbody');
                tbo.empty();
                $.each(d.rows, function(a,b){
                    inbox.find('tbody').append(create_row(b));
                });
            },
            error: function(er){
                post_error(er.responseJSON.msg, '', $('body'));
            }
        });
    }
    function create_row(d){
        var tr = $('<tr>');
        var important = 'fa fa-star';
        var attach = '';
        if(!d.is_read){
            tr.addClass('unread');
        }
        if(d.is_important){
            important += ' inbox-started';
        }
        if(d.has_attachment){
            attach = 'fa fa-paperclip';
        }
        tr.append(
        $('<td>').addClass('inbox-small-cells').append($('<input>').attr('data-read', d.is_read).attr('type', 'checkbox').attr('name', 'cbm').val(d.ext)),
        $('<td>').addClass('inbox-small-cells').data('pk', d.ext).append($('<i>').addClass(important)).on('click', function(){
            var _this = $(this);
            var st = 0;
            if(_this.find('i').hasClass('inbox-started')){
                _this.find('i').removeClass('inbox-started');
            }
            else{
                _this.find('i').addClass('inbox-started');
                st = 1;
            }
            $.ajax({
                url: '/mail/ss/?pk='+_this.data('pk')+'&st='+st,
                success: function(){
                    init_data();
                },
                error: function(er){
                    post_error(er.responseJSON.msg);
                    init_data();
                }
            })
        }),
        $('<td>').addClass('view-message dont-show').html(d.subject),
        $('<td>').addClass('view-message').html(d.message.substr(0, 50)),
        $('<td>').addClass('view-message inbox-small-cells').append($('<i>').addClass(attach)),
        $('<td>').addClass('view-message text-right').append(d.mail_date)
        );
        return tr;
    }
    init_data();
});