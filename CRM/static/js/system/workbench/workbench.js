
$(function(){
    $('[data-date=1]').persianDatepicker();
    $('#fSearchArea').on('submit', function(fs){
        fs.preventDefault();
        $('#hSearchData').val($(this).serialize());
        reloadCurrent();
    });
    $('#mRefOther').on('show.bs.modal', function(em){
        var m = $(em.target);
        var f = $('#fRefJob');
        clear_on_open(m);
        f.off('submit');
        f.on('submit', function(es){
            es.preventDefault();
            $.ajax({
                url: f.attr('action'),
                method: 'post',
                data: f.serialize(),
                success: function(){
                    reselectCurrent();
                    m.modal('hide');
                    sAlert('ارجاع انجام شد',2);
                },
                error: function(er){
                    post_error(er, null);
                }
            });
        });
        $.ajax({
            url: "/dashboard/groups/",
            method: 'get',
            dataType: 'json',
            success: function(d){
                $('#rg').empty().append($('<option>').prop({'selected': 'selected', 'disabled': 'disabled'})).change();
                $.each(d, function(a,b){
                    var o = new Option(b[0], b[0]);
                    $(o).html(b[1]);
                    $('#rg').append(o);
                })
            },
            error: function(er){
                post_error(er, null);
            }
        });
    });
    function translate(st, aic){
        var res = "معلق";
        var ic = $('<lablel>');
        if(st===1){
            res = "شروع کار";
            if (aic){
                ic.addClass('label label-default');
            }
        }
        else if(st===2){
            res = "پیگیری";
            if(aic){
                ic.addClass('label label-info');
            }
        }
        else if(st===3){
            res = "انجام شد";
            if(aic){
                ic.addClass('label label-primary');
            }
        }
        else if(st === 4){
            res = "امکان پایان وجود ندارد";
            if(aic)
            ic.addClass('label label-danger');
        }
        else if(st===5){
            res = "ارجاع شده";
            if(aic){
                ic.addClass('label label-info');
            }
        }
        else if(st===6){
            res = "کنسل شده";
            if(aic)
            ic.addClass('label label-info');
        }
        else{
            if(aic)
            ic.addClass('label label-default');
        }
        return $('<div>').append(ic.html(res)).clone().html();
    }
    initGrid({
        ajaxSettings:{
            method: 'get'
        },
        formatters: {
            'state': function(c, r){
                return translate(r.last_state, true);
            },
            'chart': function (c, r) {
                return r.done_date;
            },
            'set_pri': function(c, r){
                var s = $('<span>');
                var h = $('<span>');
                s.addClass('label');
                var x = r.fk_calendar_dashboard__priority;
                if(x==0){
                    s.addClass('label-success').html('L');
                }
                else if(x==1){
                    s.addClass('label-info').html('M');
                }
                else if(x==2){
                    s.addClass('label-danger').html('H');
                }
                else{
                    s.addClass('label-default').html('N')
                }
                h.append(s);
                h.append($('<span>').html('&nbsp&nbsp&nbsp' + r.title));
                return $('<div>').append(h.clone()).html();
            }
        },
        ajax: true,
        url_prefix: "/dashboard/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true,
        multiSelect: false,
        responseHandler: function(response){
            if(response.extra.single_user){
                $('[data-single-user=1]').removeClass('hidden').data('pk', response.extra.upk);
                $('a[data-single-user=1]').attr('href', '/user/nav/?uid='+response.extra.upk);
                $('#u').val(response.extra.upk);
            }
            else{
                $('[data-single-user=1]').addClass('hidden').data('pk', '');
                $('#u').val('');
            }
            return response;
        }
    }).on("open.grid", function(e, e2, r, summery) {
        //var rw = $('[data-row-id='+ r[0].pk+']');
        var ed = $('<div>');
        //var summery = $('<div>').addClass('row col-md-12');
        ed.addClass('row col-md-12 text-center');
        var tx = $('<table>').addClass('table table-hover').append($('<thead>').append(
            $('<tr>').append(
            $('<th>').html('#'),
            $('<th>').html('کاربر'),
            $('<th>').html('تاریخ'),
            $('<th>').html('گروه'),
            $('<th>').html('وضعیت'),
            $('<th>').addClass('soft-wrap').html('گزارش'),
            $('<th>').html('فایل'))
        ));
        $.ajax({
            url: '/dashboard/work/?d='+r[0].pk,
            method: 'get',
            dataType: 'json',
            success: function(d){
                summery.append($('<div>').addClass('ibox').append(
                    $('<div>').addClass('ibox-title').append(
                        $('<h5>').css('font-size', '12px').html('خلاصه')
                    ), $('<div>').addClass('ibox-content col-md-12').append(
                        $('<div>').addClass('col-md-4').append(
                            $('<span>').append('رویداد مربوطه : ').append($('<a>').attr('href', d.detail.target_link).attr('target', '_blank').html(d.detail.target)
                            )
                        ),
                        $('<div>').addClass('col-md-4').append(
                            $('<span>').html('پیام : ' + d.detail.message)
                        )
                    )
                )
                );
                var bStart = $('<button>').addClass('btn btn-info btn-sm margin-l4').append(
                    $('<i>').addClass('fa fa-play-circle'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('شروع')).on('click', function(){
                    sAlert('آیا از شروع این کار اطمینان دارید؟', 1, function(){
                        $.ajax({
                            url: "/dashboard/start/?sj="+r[0].pk,
                            method: 'get',
                            success: function(){
                                reselectCurrent();
                                sAlert('کار 0مورد نظر با موفقیت شروع شد', 2);
                            },
                            error: function(er){
                                post_error(er, null);
                            }
                        });
                    })
                });
                var bEnd = $('<button>').addClass('btn btn-success btn-sm margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-check'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('پایان')).on('click', function(){
                    sAlert('آیا از اتمام این کار اطمینان دارید؟', 1, function(){
                        $.ajax({
                            url: "/dashboard/start/?jd=1&sj=" + r[0].pk,
                            method: 'get',
                            success: function(){
                                reselectCurrent();
                                sAlert('کار مورد نظر با موفقیت به اتمام رسید', 2);
                            }
                        });
                    })
                });
                var bRef = $('<button>').addClass('btn btn-sm btn-success margin-l4').append(
                    $('<i>').addClass('fa fa-send'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('ارجاع')).on('click', function(){
                    var mx = $('#mRefOther');
                    mx.find('#rfj').val(r[0].pk);
                    mx.modal('show');
                });
                var bReport = $('<button>').addClass('btn btn-sm btn-info margin-l4').append(
                    $('<i>').addClass('fa fa-file-text-o'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('گزارش')).on('click', function(){
                    var mx = $('#dvAddWorkHistory');
                    mx.find('#di').val(r[0].pk);
                    mx.modal();
                });
                var bAddTime = $('<button>').addClass('btn btn-sm btn-info margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-calendar'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('تقویم')).on('click', function(){
                    var mx = $('#mAssignJob');
                    mx.find('#jb').val(r[0].pk);
                    mx.modal();
                });
                var bRemoveTime = $('<button>').addClass('btn btn-sm btn-danger margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-remove'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('حذف زمان')).on('click', function(){
                    sAlert('آیا از حذف زمان تعیین شده برای این کار اطمینان دارید؟', 1, function(){
                        $.ajax({
                            url: "/cal/rm/?d="+r[0].pk,
                            method: 'get',
                            success: function(){
                                reselectCurrent();
                                sAlert('زمانبندی با موفقیت حذف شد', 2);
                            },
                            error: function(er){
                                post_error(er, null);
                            }
                        });
                    })
                });
                var bCancel = $('<button>').addClass('btn btn-sm btn-danger margin-l4').attr('type', 'button').append(
                    $('<i>').addClass('glyphicon glyphicon-remove'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('کنسل')).on('click', function(){
                    var mx = $('#dvCancelJob');
                    mx.find('#di').val(r[0].pk);
                    mx.modal();
                });
                var bAddCall = $('<button>').addClass('btn btn-sm btn-info margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-phone'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('ثبت تماس')
                ).attr('data-pk', d.detail.user_id).attr('data-toggle', 'modal').on('click', function(){
                    var mx =$('#mAddNewCall');
                    mx.find('#u').val(d.detail.user_id);
                    mx.modal();
                });
                var bReset = $('<button>').addClass('btn btn-sm btn-info margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-refresh'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('شروع مجدد')
                ).on('click', function(){
                    sAlert('آیا از شروع مجدد این کار اطمینان دارید؟', 1, function(){
                        $.ajax({
                            url: "/dashboard/reset/?d="+r[0].pk,
                            method: 'get',
                            success: function(){
                                reselectCurrent();
                                sAlert('کار مورد نظر مجدد شروع شد', 2);
                            },
                            error: function(er){
                                post_error(er, null);
                            }
                        })
                    })
                });
                var bPartner = $('<button>').addClass('btn btn-sm btn-info margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-send'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('همکاران')
                ).on('click', function(){
                    var mx = $('#mChoosePartner');
                    mx.find('#jn').val(r[0].pk);
                    mx.modal();
                });
                var bAddTransport = $('<button>').addClass('btn btn-sm btn-info margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-plane'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('حمل و نقل')
                ).on('click', function(){
                    var mx = $('#mAddJobTransport');
                    mx.find('[name=j]').val(r[0].pk);
                    mx.modal('show');
                });
                var bRmTransport = $('<button>').addClass('btn btn-sm btn-danger margin-l4').append(
                    $('<i>').addClass('glyphicon glyphicon-plane'),
                    $('<span>').addClass('hidden-sm hidden-xs').html('حذف حمل و نقل')
                ).on('click', function(){
                    sAlert('آیا از حذف وسایل حمل و نقل برای این کار اطمینان دارید؟', 1, function(){
                        $.ajax({
                            method: 'get',
                            url: '/dashboard/transport/rm/?d='+r[0].pk,
                            success: function(){
                                reselectCurrent();
                                sAlert('حمل و نقل با موفقیت حذف شد', 2);
                            },
                            error: function(er){
                                post_error(er, null);
                            }
                        })
                    })
                });
                if(d.can_start){
                    ed.append(bStart);
                }
                if(d.can_end){
                    ed.append(bEnd);
                }
                if(d.can_cancel){
                    ed.append(bCancel);
                }
                if(d.can_ref){
                    ed.append(bRef);
                }
                if(d.can_report){
                    ed.append(bReport);
                }
                if(d.can_use_calendar){
                    ed.append(bAddTime);
                }
                if(d.can_use_calendar){
                    ed.append(bAddTime);
                }
                if(d.can_delete_calendar){
                    ed.append(bRemoveTime);
                }
                if(d.can_add_partner){
                    ed.append(bPartner);
                }
                if(d.can_choose_transport){
                    ed.append(bAddTransport);
                }
                if(d.can_delete_transport){
                    ed.append(bRmTransport)
                }
                if(d.can_add_call){
                    ed.append(bAddCall);
                }
                if(d.can_restart){
                    ed.append(bReset);
                }
                tx.append($('<tbody>'));
                $.each(d.history, function(a, b){
                    tx.find('tbody').append($('<tr>').append(
                        $('<td>').html(b[0]),
                        $('<td>').html(b[1]),
                        $('<td>').html(b[2]),
                        $('<td>').html(b[3]),
                        $('<td>').html(translate(b[4])),
                        $('<td>').addClass('soft-wrap').html(b[5]),
                        $('<td>').append($('<a>').attr({'href': '#', 'data-pk': b[6], 'data-toggle': 'modal', 'data-target': '#mUploader'}).append($('<i>').addClass('fa fa-cloud-upload')).on('click', function(ae){
                            ae.preventDefault();
                        }),$('<span>').html(' | '), $('<a>').attr({'href': '#', 'data-toggle': 'modal', 'data-target': '#mUploaded', 'data-pk': b[6]}).append($('<i>').addClass('fa fa-paperclip')).on('click', function(ae){
                            ae.preventDefault();
                        }))
                    ))
                });
                rebindModal(tx);
                summery.append(tx, ed);
            },
            error: function(er){
                post_error(er, null);
            }
        });
    });
});
