/**
 * Created by saeed on 11/10/2015.
 */
$(function(){
    load_month();
});

function load_month(mn, yr){
    var dxs = $('[data-bsc-days=1]');
    dxs.empty();
    $.ajax({
        url: "/cal/today/?m=" + mn + "&y=" + yr,
        method: 'get',
        success: function(d){
            $('#sDay').html(d.today_month_name + ' ' + d.year);
            $('#hNext').val(d.next_month);
            $('#hBack').val(d.last_month);
            $('#hYear').val(d.next_year);
            $('#hBackYear').val(d.last_year);
            var newTr = $('<tr></tr>');
            var week_day_start = d['data'][0].week_day+2;
            if(week_day_start == 7){
                week_day_start = 0;
            }
            else if(week_day_start > 6){
                week_day_start = 1;
            }
            else if(week_day_start < 2){
                week_day_start = 0;
            }
            var padding = false;

            for(var i0=0; i0< week_day_start;i0+=1){
                newTr.append(BSCalendarCreateCell('', '', false));
                padding = true;
            }
            if(padding)
                dxs.append(newTr);
            $.each(d.data, function(a,b){
                if((b.week_day+2)%7==0){
                    dxs.append(newTr);
                    newTr = $('<tr></tr>');
                }
                newTr.append(BSCalendarCreateCell(b.day, d.today_day,
                    b.is_weekend, b.current_load, b.month, d.now_day, d.now_month,
                    b.year, d.now_year, b.total_jobs));
            });
            dxs.append(newTr);
            load_events();
        },
        dataType: 'json'
    });
}

function load_events(){
    $('[data-next=1]').off().on('click', function(){
        load_month($('#hNext').val(), $('#hYear').val());
    });
    $('[data-back=1]').off().on('click', function(){
        load_month($('#hBack').val(), $('#hBackYear').val());
    });
    $('.label-info').on('click', function(e){

    });
}

function BSCalendarCreateCell(day, today, is_weekend, free_time, month, nd, nm, today_year, ny, total_jobs){
    var td = $('<td></td>');
    var s_day = $('<h1></h1>');
    s_day.addClass('BSCalendar-Cell-Text').html(day);
    var a = $('<a></a>');
    a.addClass('pull-left').addClass('glyphicon').addClass('glyphicon-search').attr('href', '/dashboard/?cal='+ today_year+'/'+month+'/'+day);
    var free_time_holder = $('<div></div>');
    free_time_holder.addClass('progress');
    var free_time_progress = $('<div></div>');
    free_time_progress.addClass('progress-bar');
    free_time_progress.attr('role', 'progressbar');
    free_time_progress.attr('aria-valuenow', 0);
    free_time_progress.attr('aria-valuemin', 0);
    free_time_progress.attr('aria-valuemax', total_jobs);
    free_time_progress.attr('style', 'width:'+free_time+'%');
    free_time_holder.append(free_time_progress);
    var task_count = $('<span></span>');
    task_count.addClass('label').addClass('label-info').addClass('pull-right');
    task_count.html(free_time);
    var tasks = $('<div></div>');
    if((today_year > ny)|| month>=nm){
        tasks.append(free_time_holder);
    }
    tasks.append(task_count);
    if(day !== '')
        tasks.append(a);
    tasks.addClass('BSCalendar-task');
    if(is_weekend){
        td.addClass('BSCalendar-weekend');
    }
    else if(day === ''){
        td.addClass('BSCalendar-day-empty');
    }
    else if(nd === day && month === nm){
        td.addClass('BSCalendar-today');
    }
    var task_holder = $('<div></div>');
    task_holder.addClass('BSCalendar-tasks');
    task_holder.append(tasks);
    td.append(s_day);
    td.append(task_holder);
    td.addClass('BSCalendar-cell').addClass('row').addClass('col-md-2');
    return td;
}