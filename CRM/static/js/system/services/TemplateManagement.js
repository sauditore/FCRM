/**
 * Created by saeed on 4/7/16.
 */

$(function () {
    $('#mView').on('show.bs.modal', function(me){
        var $this = $(this);
        var t = $('#tViewHolder').find('tbody').empty();
        $.ajax({
            url: '/service/float/template/options/?pk='+$(me.relatedTarget).data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(b){
                $.each(b, function(a, d){
                    t.append(
                        $('<tr>').append(
                            $('<td>').html(d.pk),
                            $('<td>').html(d.option__name),
                            $('<td>').append($('<span>').addClass('price').html(d.price)),
                            $('<td>').html(d.value),
                            $('<td>').append($('<span>').addClass('price').html(d.total_price))
                        )
                    );
                });
                formatPrice($this);
            },
            error: function(er){
                post_error(er)
            }
        });
    });
    initGrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            'test_action': function(c,r){
                var b = $('<label>').addClass('label');
                var i = $('<i>').addClass('fa');
                if(c.id=='is_public_test'){
                    if(r.is_public_test){
                        b.addClass('label-danger');
                        i.addClass('fa-check');
                    }else{
                        i.addClass('fa-remove');
                        b.addClass('label-info');
                    }
                }
                else{
                    if(r.is_test){
                        b.addClass('label-danger');
                        i.addClass('fa-check');
                    }else{
                        i.addClass('fa-remove');
                        b.addClass('label-info');
                    }
                }
                b.append(i);
                return $('<div>').append(b).html();
            }
        },
        ajax: true,
        url_prefix: "/service/float/template/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function (e, e2, r, summery) {
        var a = $('<div>').addClass('text-center').append(getActionArea());
        summery.append(a);
        rebindModal(summery);
        summery.find('[data-need-pk]').data('pk', r[0].ext);
        bindDelete(summery);
        bindEdit(summery);
        if(r[0].is_test){
            bindPublicTest(summery);
        }
        summery.find('[data-action="ed"]').on('click', function(ae){
            ae.preventDefault();
            document.location = $(this).attr('href')+$(this).data('pk');
        });
    });
    function bindPublicTest(sm){
        sm.find('[data-edit=2]').removeClass('hidden').on('click', function(){
            var $this = $(this);
            $.ajax({
                url: '/service/float/template/toggle_public/?pk='+$this.data('pk'),
                method: 'get',
                success: function(){
                    reloadCurrent();
                },
                error: function(er){
                    post_error(er);
                }
            })
        });
    }
    function bindEdit(sm){
        sm.find('[data-edit=1]').on('click', function(){
            var $this = $(this);
            $.ajax({
                url: '/service/float/template/toggle/?pk='+ $this.data('pk'),
                method: 'get',
                success: function(){
                    reloadCurrent();
                },
                error: function(er){
                    post_error(er, null, null);
                }
            })
        });
    }
});
