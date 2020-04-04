/**
 * Created by saeed on 3/22/16.
 */
$(function(){
    //var doughnutData = [
    //    {
    //        value: 2000-1350,
    //        color: "#a3e1d4",
    //        highlight: "#1ab394",
    //        label: "فعال"
    //    },
    //    {
    //        value: 1350,
    //        color: "blue",
    //        highlight: "darkblue",
    //        label: "آنلاین"
    //    }
    //];
    //var doughnutOptions = {
    //
    //    segmentShowStroke: true,
    //    segmentStrokeColor: "#fff",
    //    segmentStrokeWidth: 2,
    //    percentageInnerCutout: 40, // This is 0 for Pie charts
    //    animationSteps: 100,
    //    animationEasing: "easeOutBounce",
    //    animateRotate: true,
    //    animateScale: false
    //};
    //var personnelData = [
    //    {
    //        value: 25,
    //        color: "#a3e1d4",
    //        highlight: "#1ab394",
    //        label: "غیرفعال"
    //    },
    //    {
    //        value: 5,
    //        color: "blue",
    //        highlight: "darkblue",
    //        label: "آنلاین"
    //    }
    //];
    //var personnelOptions = {
    //
    //    segmentShowStroke: true,
    //    segmentStrokeColor: "#fff",
    //    segmentStrokeWidth: 2,
    //    percentageInnerCutout: 40, // This is 0 for Pie charts
    //    animationSteps: 100,
    //    animationEasing: "easeOutBounce",
    //    animateRotate: true,
    //    animateScale: false
    //};
    //var ctx = document.getElementById("dOnlineCustomer").getContext("2d");
    //var cc = new Chart(ctx).Doughnut(doughnutData, doughnutOptions);
    //var ctx2 = document.getElementById('dOnlinePersonnel').getContext("2d");
    //var pc = new Chart(ctx2).Doughnut(personnelData, personnelOptions);
    //setInterval(function(){
    //    pc.segments[1].value = parseInt(pc.segments[1].value) + 1;
    //    pc.update();
    //}, 1000);
    var data1 = [];
    var data2 = [];
    if($("#dSells").length < 1){
        return
    }
    $.ajax({
        url: '/factor/graph_analyze/',
        method: 'get',
        dataType: 'json',
        success: function(d){
            $.each(d[0], function(a,b){
                data1.push([b[1], b[0]]);
            });
            $.each(d[1], function(a,b){
                data2.push([b[1], b[0]]);
            });
            $.plot($("#dSells"), [
                data1,  data2
            ],
                {
                    series: {
                        lines: {
                            show: true,
                            fill: true
                        },
                        splines: {
                            show: false,
                            tension: 0.4,
                            lineWidth: 1,
                            fill: 0.4
                        },
                        points: {
                            radius: 0,
                            show: true
                        },
                        shadowSize: 2
                    },
                    grid: {
                        hoverable: true,
                        clickable: true,

                        borderWidth: 2,
                        color: 'transparent'
                    },
                    colors: ["green", "silver"],
                    xaxis:{
                        //zoomRange: [0.1, 10],
				        //panRange: [-10, 10]
                    },
                    yaxis: {
                        //zoomRange: [0.1, 10],
				        //panRange: [-10, 10]
                    },
                    zoom: {
                        interactive: true
                    },
                    pan: {
                        interactive: true
                    },
                    tooltip: false
                }
            );
        },
        error: function(e){
            post_error(e);
        }
    });

});