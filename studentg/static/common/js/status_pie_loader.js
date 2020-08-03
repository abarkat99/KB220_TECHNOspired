var $grievance_status_chart = $("#grievance-status-chart");
var $grievance_subcat_chart = $("#grievance-subcat-chart");
function chart_ajax($chart){
    if ($chart.data("tooltip-type") == "percent") {
        var tooltip_callbacks = {
            label: function(tooltipItem, data) {
                var indice = tooltipItem.index;
                var label = data.labels[indice] + ': '+ (Math.round((data.datasets[0].data[indice] + Number.EPSILON) * 100) / 100) + ' %';
                return label;
            }
        };
    } else {
        var tooltip_callbacks = {};
    }
    if($chart.data("color") == "auto") {
        var plugins = {
            colorschemes: {
                scheme: 'tableau.Classic20'
              }
        }
    }
    $.ajax({
        url: $chart.data("url"),
        success: function (data) {
            var ctx = $chart[0].getContext("2d");
            new Chart(ctx, {
                type: 'pie',
                data: data,
                options: {
                        legend: {
                            onClick: (e) => e.stopPropagation()
                        },
                        tooltips: {
                            callbacks: tooltip_callbacks
                        },
                        plugins: plugins
                    }
            });
        },
        error: function () {
            console.log('Something Went Wrong!');
        }
    });
}
chart_ajax($grievance_status_chart);
chart_ajax($grievance_subcat_chart);