$(function () {
    var tin = $('#tData');
    var mad = $('#mAdd');
    var fad = $('#fAdd');
    var fsr = $('#fSR');
    var msr = $('#mSR');
    msr.on('show.bs.modal', function(me){
        var btn = $(me.relatedTarget);
        msr.find('[name=pk]').val(btn.data('pk'));
    });
    fsr.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/indicator/sr/?',
            data: fsr.serialize(),
            method: 'get',
            success: function(){
                reload_grid(tin);
                msr.modal('hide');
            },
            error: function(er){
                post_error(er.responseJSON.msg, er.responseJSON.param, msr);
            }
        })
    });
    $('[data-date=1]').persianDatepicker();
    mad.on('show.bs.modal', function(me){
        clear_on_open(mad);
        var btn = $(me.relatedTarget);
        if(btn.data('pk')!=undefined){
            $.ajax({
                url: '/indicator/j/?pk='+btn.data('pk'),
                method: 'get',
                 dataType: 'json',
                success: function(d){
                    mad.find('[name=pk]').val(d.ext);
                    mad.find('[name=sd]').val(d.send_date);
                    mad.find('[name=t]').val(d.person);
                    mad.find('[name=s]').val(d.title);
                    mad.find('[name=ha]').prop('checked', d.has_attachment);
                    mad.find('[name=lf]').val(d.letter);
                    mad.find('[name=pb]').val(d.pocket);
                    mad.find('[name=bt]').val(d.book_type);
                },
                error: function(er){
                    post_error(er.responseJSON.msg, er.responseJSON.param, mad);
                }
            });
        }
    });
    fad.on('submit', function(fs){
        fs.preventDefault();
        $.ajax({
            url: '/indicator/add/',
            method: 'post',
            data: fad.serialize(),
            success: function(){
                mad.modal('hide');
                reload_grid(tin);
            },
            error: function(er){
                post_error(er.responseJSON.msg, er.responseJSON.param, mad);
            }
        });
    });
    tin.bootgrid({
        ajaxSettings: {
            method: 'get'
        },
        formatters: {
            bool: function a(a,b){
                return translate_bool(b.has_attachment);
            },
            letter_type: function(a,b){
                if(b.book_type == 0){
                    return 'ارسالی'
                }
                else{
                    return 'دریافتی'
                }
            }
        },
        ajax: true,
        url: function () {
            return "/indicator/";
        },
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    }).on('selected.rs.jquery.bootgrid', function (e, r) {
        $('[data-need-pk=1]').data('pk', r[0].ext).not('[data-manual]').removeClass('hidden');
        if(r[0].receive_date == null){
            $('[data-target="#mSR"]').removeClass('hidden');
        }
        else{
            $('[data-target="#mSR"]').addClass('hidden');
        }
        $('#spc').html(r[0].title);
    });
});