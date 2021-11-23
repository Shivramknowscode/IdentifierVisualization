var plot_width = 500;
var plot_height = 500;
var margin_l = 100;
var margin_r = 100;
marker_size = 0.5; // x-axis units
xaxis_start = 1;
xaxis_stop = 5;

var trace1 = {
  x: [1.5, 2, 3, 4],
  y: [10, 15, 13, 17],
  mode: "markers",
  marker: {
    size: marker_size *
      (plot_width - margin_l - margin_r) /
      (xaxis_stop - xaxis_start)
  },
  showlegend: false
};

var trace2 = {
  x: [2, 3, 4, 4.5],
  y: [16, 5, 11, 10],
  mode: "lines"
};

var trace3 = {
  x: [1.5, 2, 3, 4],
  y: [12, 9, 15, 12],
  mode: "lines+markers",
  showlegend: false
};

var data = [trace1, trace2, trace3];

var layout = {
  width: plot_width,
  height: plot_height,
  margin: {
    l: margin_l,
    r: margin_r
  },
  xaxis: {
    range: [1, 5]
  },
  showlegend: false
};

Plotly.newPlot("myDiv", data, layout);

var refplot = document.getElementById("myDiv");
refplot.on("plotly_relayout", function(eventdata) {
  if (eventdata["xaxis.range[1]"] !== undefined) {
    var update = {
      "marker.size": marker_size *
        (plot_width - margin_l - margin_r) /
        (eventdata["xaxis.range[1]"] - eventdata["xaxis.range[0]"])
    };
  } else {
    var update = {
      "marker.size": marker_size *
        (plot_width - margin_l - margin_r) /
        (xaxis_stop - xaxis_start)
    };
  }
  Plotly.restyle("myDiv", update, 0);
});
