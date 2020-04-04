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
                    post_error(er, null, mad);
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
                post_error(er, null, mad);
            }
        });
    });
    initGrid({
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
        url_prefix: "/indicator/",
        labels: {
            all: "همه",
            infos: "نمایش {{ctx.start}} تا {{ctx.end}} از {{ctx.total}}",
            noResults: 'هیچ نتیجه ای وجود ندارد',
            search: 'جستجو',
            loading: 'درحال بارگزاری'
        },
        selection: true,
        rowSelect: true
    });
    getCurrentGrid().on('open.grid', function(a,b,r,summery){
        summery.append($('<div>').append(//Main Dive
            $('<h3>').append(// Title Holder
                $('<i>').addClass('fa fa-info-circle').css('margin-left', '5px'), $('<span>').html('موضوع')
            ),
            $('<div>').html(r[0].title)
        )
            //$('#dACTS').clone().css('display', 'block')
        );
        summery.append(getActionArea);
        if(r[0].receive_date == null){
            summery.find('[data-target="#mSR"]').removeClass('hidden');
        }
        else{
            summery.find('[data-target="#mSR"]').addClass('hidden');
        }
        rebindModal(summery);
        //loadEvent();
        bindDelete(summery);
        summery.find('[data-need-pk=1]').data('pk', r[0].ext).not('[data-manual]').removeClass('hidden');
    });
});
