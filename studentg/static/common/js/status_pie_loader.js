var $grievance_status_chart = $("#grievance-status-chart");
$.ajax({
    url: $grievance_status_chart.data("url"),
    success: function (data) {
        var ctx = $grievance_status_chart[0].getContext("2d");
        new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                    legend: {
                        onClick: (e) => e.stopPropagation()
                    }
                }
        });
    },
    error: function () {
        console.log('Something Went Wrong!');
    }
});