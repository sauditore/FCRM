/**
 * Created by saeed on 5/9/16.
 */

$(function(){
    var m = $('#mAssignTemplate');
    var f = m.find('form');
    var su = f.find('#sUsersAuto');
    var tu = f.find('#sTowerAuto');
    m.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        m.find('[name=pk]').val(btn.data('pk'));
    });
    f.off('submit').on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: f.attr('action'),
            method: 'get',
            data: f.serialize(),
            success: function(){
                m.modal('hide');
                sAlert('عملبات با موفقیت انجام شد', 2);
            },
            error: function(er){
                post_error(er);
            }
        });
    });
    tu.css('width', '100%').select2({
        dir: 'rtl',
        placeholder: "برج",
        ajax: {
            url: '/tower/au/',
            dataType: 'json',
            delay: 500,
            data: function (params) {
                return {
                    query: params.term, // search term
                    page: params.page
                    };
            },
            processResults: function(data){
                var res = [];
                $.each(data, function(a,b){
                    res.push({text: b.name, id: b.id})
                });
                return {
                    results: res,
                    pagination: {}
                };
            }
        }
    });
    su.css('width', '100%').select2({
        dir:'rtl',
        placeholder: 'کاربر',
        ajax: {
            url: '/user/au/',
            dataType: 'json',
            delay: 500,
            data: function (params) {
                return {
                    query: params.term, // search term
                    page: params.page
                    };
            },
            processResults: function(data){
                var res = [];
                $.each(data, function(a,b){
                    //noinspection JSUnresolvedVariable
                    res.push({text: b.first_name, id: b.id})
                });
                return {
                    results: res,
                    pagination: {}
                };
            }
        }
    });
});
