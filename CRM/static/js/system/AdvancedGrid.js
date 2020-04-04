/**
 * Created by saeed on 4/3/16.
 */
var page_grid = null;
function getCurrentGrid(){
    return page_grid;
}
function reloadCurrent(){
    page_grid.bootgrid('reload');
}
function reselectCurrent(){
    var s = page_grid.bootgrid('getSelectedRows');
    page_grid.bootgrid('deselect');
    setTimeout(function(){
        page_grid.bootgrid('select', s);
    }, 2000);
}
function initGrid(options){
    if($('#fSdx').length){
        options['url'] = function(){
            var pfx = options['url_prefix'];
            if(!pfx.endsWith('?'))
                if(pfx.indexOf('?')<0){
                    pfx += '?';
                }
            return pfx+$('#fSdx').val();
        }
    }
    page_grid = $('[data-toggle="grid"]').bootgrid(options);
    page_grid.on('selected.rs.jquery.bootgrid', function(e,r){
        var rw = $('[data-row-id='+ r[0].pk+']').addClass('selected-grid');
        var summery = $('<div>').addClass('row col-md-12 collapse').attr('data-inner','1');
        var td = $('<td>').addClass('no-padding gradient-bg');
        td.attr('colspan', rw.find('td').size()).append(summery).addClass('opened-grid');
        var float_data = $('<tr>').data('extra', '1');
        float_data.append(td);
        rw.after(float_data);
        summery.addClass('animated fadeIn gradient-bg no-margins');
        var is_beak = false;
        var refreshId = setInterval(function() {
            if(is_beak){
                clearInterval(refreshId);
            }
        }, 100);
        setTimeout(function(){
        $.when(page_grid.trigger('open.grid', [e, r, summery])).done(function(){
            summery.addClass('in');
            is_beak = true;
        });
        }, 350);

    }).on('deselected.rs.jquery.bootgrid', function(e, r){
        var rw = $('[data-row-id='+ r[0].pk+']').removeClass('selected-grid');
        var smx = rw.next().find('[data-inner=1]');
        smx.removeClass('fadeIn').addClass('zoomOut');
        setTimeout(function(){
            smx.on('hide.bs.collapse', function(){
                setTimeout(function(){
                    smx.parent().parent().remove();
                }, 150);
            });
            smx.collapse('hide');
            page_grid.find('tr').removeClass('hidden');
        }, 150);
        page_grid.trigger('close.grid', [e, r, rw]);
    }).on('loaded.rs.jquery.bootgrid', function(){
        page_grid.trigger('loaded.grid');
    });
    return page_grid;
}
