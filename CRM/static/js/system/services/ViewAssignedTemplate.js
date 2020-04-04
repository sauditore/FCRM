/**
 * Created by saeed on 5/9/16.
 */

$(function(){
    var m = $('#mViewAssigned');
    var f = m.find('form');
    m.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        f.find('[name=u]').val(btn.data('pk'));
        $.ajax({
            url: '/service/float/template/user/',
            data: 'u='+btn.data('pk'),
            dataType: 'json',
            success: function(d){
                var t = m.find('tbody');
                t.empty();
                $.each(d, function(a,b){
                    var fxx = $('<form>').attr('action', '/service/float/buy/invoice/').attr('method', 'post');
                    fxx.append(
                        $('<input>').attr({'type': 'hidden', 'name': 'u', 'value': btn.data('pk')}),
                        $('<input>').attr({'type': 'hidden', 'name': 'utm', 'value': b.ext}),
                        $('<button>').attr('type', 'submit').addClass('btn btn-xs btn-success').append($('<i>').addClass('fa fa-shopping-cart')),
                        $('<span>').html(' '),
                        $('<button>').attr({'type': 'button', 'data-toggle': 'view', 'data-pk': b.ext}).addClass('btn btn-xs btn-primary').append($('<i>').addClass('fa fa-list')).on('click', function(){
                            var $this = $(this);
                            $.ajax({
                                url: '/service/float/template/options/?pk='+$this.data('pk'),
                                method: 'get',
                                dataType: 'json',
                                success: function(d1){
                                    var p = $this.parents().find('tr').has($this);
                                    var $tr = $('<tr>');
                                    var $th = $('<tr>').append(
                                        $('<th>').html('نام'),
                                        $('<th>').html('هزینه'),
                                        $('<th>').html('مقدار'),
                                        $('<th>').html('هزینه کل')
                                    );
                                    var $tb = $('<table>').addClass('table table-bordered').append($('<thead>').append($th));
                                    $.each(d1, function(a,b){
                                        $tb.append(
                                            $('<tbody>').append(
                                                $('<tr>').append(
                                                    $('<td>').html(b.option__name),
                                                    $('<td>').html(get_price_cell_formatter(b.price, true)),
                                                    $('<td>').html(b.value),
                                                    $('<td>').html(get_price_cell_formatter(b.total_price, true))
                                                )
                                            )
                                        )
                                    });
                                    $tr.append(
                                        $('<td>').attr('colspan', 5).append(
                                            $('<div>').append(
                                                $tb
                                            )
                                        )
                                    );
                                    p.after($tr);
                                    $this.remove();

                                },
                                error: function(er){
                                    post_error(er, null, fxx);
                                }
                            })
                        })
                    );
                    t.append(
                        $('<tr>').append(
                            $('<td>').html(b.name),
                            $('<td>').addClass('hidden-xs').html(b.service__name),
                            $('<td>').append(get_price_cell_formatter(b.final_price, false, false)),
                            $('<td>').html(b.service_period + ' ماه'),
                            $('<td>').append(
                                fxx
                            )
                        )
                    );
                })
            },
            error: function(er){
                post_error(er, null, m);
            }
        })
    });
});