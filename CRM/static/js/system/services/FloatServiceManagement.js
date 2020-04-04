$(function () {
    var tsr = $('#tFloatService');
    var tsf = $('#tServiceFormula');
    var maf = $('#mAddFormula');
    var faf = $('#fAddFormula');
    var mab = $('#mAddNewBasicService');
    var fab = $('#fAddNewBasicService');
    var tco = $('#tCustomOptions');
    var mco = $('#mAddCustomOption');
    var fco = $('#fAddCustomOption');
    var opt = $('#sOptions');
    var mpt = $('#mAssignOption');
    var fpt = $('#fAssignOption');
    var msm = $('#mMapService');
    var fsm = $('#fMapService');
    var bAdd = msm.find('#bAdd');
    var sSr = $('#sbs');
    var sih = $('#sih');
    var mAssign = $('#mAssignDefault');
    var fAssign = $('#fAssignDefault');
    mAssign.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mAssign.find('[name=pk]').val(btn.data('pk'));
    });
    fAssign.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/service/float/default/?'+fAssign.serialize(),
            method: 'get',
            success: function(){
                mAssign.modal('hide');
                sAlert('عملیات با موفقیت انجام شد',2);
            },
            error:function(er){
                post_error(er, null, fAssign);
            }
        })
    });
    msm.on('show.bs.modal', function(me){
        bAdd.data('pk', $(me.relatedTarget).data('pk'));
        msm.find('#holder').empty();
        var bPk = bAdd.data('pk');
        $.ajax({
            url: '/service/float/option/service/j/?pk='+bAdd.data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(d){
                $.each(d, function(a,b){
                    var l = $('<button>').addClass('btn btn-sm btn-info').data({'o':bPk, 's': b.service__ext, 'i': b.group__ext}).attr('type', 'button');
                    l.html(b.group__name + ' و ' + b.service__name).on('click', function(){
                        var _that = $(this);
                        $.ajax({
                            url: '/service/float/option/service/add/?d=1&pk='+_that.data('o')+'&s='+_that.data('s')+'&i='+_that.data('i'),
                            success: function(){
                                _that.parent().remove();
                                sAlert('آیتم مورد نظر حذف شد',2);
                            },
                            error: function(er){
                                post_error(er, null);
                            }
                        });
                    });
                    fsm.find('#holder').append($("<div>").addClass('form-group').append(l));
                });
            },
            error: function(er){
                post_error(er, null, msm);
            }
        });
    });
    bAdd.on('click', function(){
        var tsi = sih.find(':selected');
        var tss = sSr.find(':selected');
        var bPk = bAdd.data('pk');
        if(fsm.find('[data-s*='+tss.val()+']').length){
            show_error('این سرویس قبلا انتخاب شده است');
            return;
        }
        $.ajax({
            url: '/service/float/option/service/add/?pk='+bAdd.data('pk')+'&s='+tss.val()+'&i='+tsi.val(),
            method: 'get',
            success: function(){
                var l = $('<button>').addClass('btn btn-sm btn-info').data({'o':bPk, 's': tss.val(), 'i': tsi.val()}).attr('type', 'button');
                l.html(tsi.text() + ' و '+tss.text()).on('click', function(){
                    var _that = $(this);
                    $.ajax({
                        url: '/service/float/option/service/add/?d=1&pk='+_that.data('o')+'&s='+_that.data('s')+'&i='+_that.data('i'),
                        success: function(){
                            _that.parent().remove();
                            sAlert('آیتم مورد نظر حذف شد',2);
                        }
                    });
                });
                fsm.find('#holder').append($("<div>").addClass('form-group').append(l));
            },error:function(er){
                post_error(er, null, msm);
            }
        });
    });

    $('#mrs').on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        var that = $(this);
        that.find('[name=pk]').val(btn.data('pk'));
        $.ajax({
            url: '/service/float/related/j/?pk='+btn.data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(d){
                var o = that.find('[name=gr]');
                o.find('option').prop('selected', false);
                $.each(d, function(a,b){
                    o.find('[value='+b+']').prop('selected', true);
                });
                o.change();
            },
            error: function(er){
                post_error(er, null, $(this));
            }
        });
        that.find('form').off('submit').on('submit', function(fs){
            fs.preventDefault();
            var _this = $(this);
            $.ajax({
                method: 'post',
                url: '/service/float/related/add/',
                data: _this.serialize(),
                success: function(){
                    that.modal('hide');
                    sAlert('عملیات با موفقیت انجام شد',2);
                },
                error: function(er){
                    post_error(er, null, _this);
                }
            })
        });
    });
    $('#importIBS').on('click', function(){
        sAlert('',1, function(){
            $.ajax({
                url:'/service/import/',
                method: 'get',
                success: function(){
                    sAlert('سرویس ها با موفقیت وارد شدند',2);
                },
                error: function(er){
                    post_error(er);
                }
            });
        });
    });
    mpt.off().on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        opt.empty();
        var selected = [];
        mpt.find('[name=pk]').val(btn.data('pk'));
        $.ajax({
            url: '/service/float/options/?pk='+btn.data('pk'),
            method: 'get',
            dataType: 'json',
            success: function(d){
                selected = d;
            },
            error: function(er){
                post_error(er, null, mpt);
            }
        });
        $.ajax({
            url: '/service/float/option/?current=1&rowCount=-1',
            dataType: 'json',
            success: function(d){
                $.each(d.rows, function(a,b){
                    var o = $('<option>');
                    o.val(b.ext).html(b.name);
                    if($.inArray(b.ext, selected) > -1){
                        o.prop('selected', true);
                    }
                    opt.append(o);
                });
                opt.trigger('change');
            },
            error: function(er){
                post_error(er,null, mpt);
            }
        });
        fpt.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/service/float/assign/',
                method: 'post',
                data: fpt.serialize(),
                success: function(){
                    tsr.bootgrid('reload');
                    mpt.modal('hide');
                },
                error: function(er){
                    post_error(er,null, mpt);
                }
            })
        });
    });
    mco.off().on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mco.find('input[type=text]').val('');
        mco.find('select').val('');
        mco.find('[name=pk]').val('');
        if(btn.data('pk')!=undefined){
            mco.find('[type=hidden]').val(btn.data('pk'));
            $.ajax({
                url: '/service/float/option/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    mco.find('[name=n]').val(d.name);
                    mco.find('[name=i]').val(d.min_value);
                    mco.find('[name=a]').val(d.max_value);
                    mco.find('#sServices').val(d.group_type);
                    mco.find('#sPack').val(d.package);
                    mco.find('[name=vn]').val(d.var_name);
                    mco.find('[name=og]').val(d.group);
                    mco.find('[name=ip]').val(d.pool);
                    mco.find('[name=ht]').html(d.help_text);
                    if(d.is_custom_value){
                        mco.find('[name=cf]').attr('checked', 'checked').val('1');
                    }
                    else{
                        mco.find('[name=cf]').removeAttr('checked');
                    }
                    mco.find('[name=cfi]').val(d.custom_value_min);
                    mco.find('[name=cfx]').val(d.custom_value_max);
                    $.ajax({
                        url: '/service/float/buy/related/?t=pk&pk='+btn.data('pk'),
                        method: 'get',
                        dataType: 'json',
                        success: function(d){
                            mco.find('#sRel > option').each(function(a, b){
                                if($.inArray(parseInt($(b).val()), d) > -1){
                                    $(b).attr('selected', 'selected');
                                }
                            });
                            mco.find('#sRel').change();
                        },
                        error: function(er){
                            post_error(er, null, mco);
                        }
                    });
                },
                error: function(er){
                    post_error(er, null, mco);
                }
            });
        }
        fco.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/service/float/option/add/',
                method: 'post',
                data: fco.serialize(),
                success: function(){
                    reloadCurrent();
                    mco.modal('hide');
                    sAlert('عملیات با موفقیت انجام شد', 2);
                },
                error: function(er){
                    post_error(er, null, mco);
                }
            });
        });
    });
    if(tco.length){
        initGrid({
            ajaxSettings: {
                method: 'get'
            },
            formatters: {
                'is_custom': function(c,r){
                    var i = $('<i>').addClass('fa');
                    if(r.is_custom_value){
                        i.addClass('fa-check text-success');
                    }
                    else{
                        i.addClass('fa-remove text-danger');
                    }
                    return $('<div>').append(i).html();
                },
                'service_type': function(c,r){
                    if(r.group_type==1){
                        return 'محدود'
                    }
                    else if(r.group_type == 2){
                        return 'نامحدود'
                    }
                    else{
                        return 'بی تاثیر'
                    }
                }
            },
            ajax: true,
            url_prefix: "/service/float/option/",
            labels: {
                all: "همه",
                infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
                noResults: 'هیچ نتیجه ای وجود ندارد',
                search: 'جستجو',
                loading: 'درحال بارگزاری'
            },
            selection: true,
            rowSelect: true
        }).on('open.grid', function (e,e2, r, summery) {
            summery.append(getActionArea());
            summery.find('[data-need-pk=1]').data('pk', r[0].ext);
            rebindModal(summery);
            bindDelete(summery);
        });
    }
    mab.off().on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        mab.find('input').val('');
        if(btn.data('pk')!=undefined){
            $('[type=hidden]').val(btn.data('pk'));
            $.ajax({
                url: '/service/float/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    mab.find('[name=n]').val(d.name);
                    mab.find('[name=b]').val(d.base_ratio);
                    mab.find('[name=i]').val(d.service_index);
                    mab.find('#sFormula').val(d.formula);
                    mab.find('[name=bw]').val(d.bw);
                },
                error: function(er){
                    post_error(er,null, mab);
                }
            });
        }
        fab.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/service/float/add/',
                method: 'post',
                data: fab.serialize(),
                success: function(){
                    reloadCurrent();
                    mab.modal('hide');
                },
                error: function(er){
                    post_error(er,null, mab);
                }
            });
        });
    });
    maf.off().on('show.bs.modal', function(ms){
        maf.find('[name=n]').val('');
        maf.find('[name=f]').html('');
        var btn = $(ms.relatedTarget);
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/service/float/formula/j/?pk='+btn.data('pk'),
                method: 'get',
                dataType: 'json',
                success: function(d){
                    maf.find('[name=n]').val(d.name);
                    maf.find('[name=f]').html(d.formula);
                    maf.find('[type=hidden]').val(d.ext);
                },
                error: function(er){
                    post_error(er,null, maf);
                }
            });
        }
        faf.off('submit').on('submit', function(fs){
            fs.preventDefault();
            $.ajax({
                url: '/service/float/formula/add/',
                method: 'post',
                data: faf.serialize(),
                success: function(){
                    reloadCurrent();
                    maf.modal('hide');
                    sAlert('عملیات با موفقیت انجام شد', 2);
                },
                error: function(er){
                    post_error(er, null, maf);
                }
            });
        })
    });
    if(tsf.length){
        initGrid({
            ajaxSettings: {
                method: 'get'
            },
            formatters: {},
            ajax: true,
            url_prefix: "/service/float/formula/",
            labels: {
                all: "همه",
                infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
                noResults: 'هیچ نتیجه ای وجود ندارد',
                search: 'جستجو',
                loading: 'درحال بارگزاری'
            },
            selection: true,
            rowSelect: true
        }).on('open.grid', function (e,e2, r, summery) {
            summery.append(getActionArea());
            rebindModal(summery);
            bindDelete(summery);
            summery.find('[data-need-pk=1]').data('pk', r[0].ext);
        });
    }
    if(tsr.length){
        initGrid({
            ajaxSettings: {
                method: 'get'
            },
            formatters: {},
            ajax: true,
            url_prefix: "/service/float/",
            labels: {
                all: "همه",
                infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
                noResults: 'هیچ نتیجه ای وجود ندارد',
                search: 'جستجو',
                loading: 'درحال بارگزاری'
            },
            selection: true,
            rowSelect: true
        }).on('open.grid', function (e,e2, r, summery) {
            summery.append(getActionArea);
            rebindModal(summery);
            bindDelete(summery);
            summery.find('[data-need-pk=1]').data('pk', r[0].ext);
        });
    }
});