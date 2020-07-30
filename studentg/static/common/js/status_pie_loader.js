var $grievance_status_chart = $("#grievance-status-chart");
$.ajax({
    url: $grievance_status_chart.data("url"),
    success: function (data) {
        var ctx = $grievance_status_chart[0].getContext("2d");
        if ($grievance_status_chart.data("tooltip-type") == "percent") {
            var tooltip_callbacks = {
                label: function(tooltipItem, data) {
                    var indice = tooltipItem.index;
                    var label = data.labels[indice] + ': '+ data.datasets[0].data[indice] + ' %';
                    return label;
                }
            };
        } else {
            var tooltip_callbacks = {};
        }
        new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                    legend: {
                        onClick: (e) => e.stopPropagation()
                    },
                    tooltips: {
                        callbacks: tooltip_callbacks
                    }
                }
        });
    },
    error: function () {
        console.log('Something Went Wrong!');
    }
});