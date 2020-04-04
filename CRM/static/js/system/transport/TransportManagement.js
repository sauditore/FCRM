/**
 * Created by saeed on 5/2/16.
 */

$(function(){
    initGrid({
        ajax: true,
        ajaxSettings: {
            method: 'get'
        },
        url_prefix: "/transport/",
        labels: {
            all: "همه",
            infos: ""
        },
        selection: true,
        rowSelect: true
    }).on('open.grid', function(e,e2, r, summery){
        summery.append(getActionArea());
        summery.find('[data-need-pk=1]').data('pk', r[0].ext);
    });
});