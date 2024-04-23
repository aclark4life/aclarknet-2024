import Chart from "chart.js/auto";

// Declare an array to store chart instances
var charts = [];

// Function to render charts
function renderCharts() {
  // Loop through all chart instances and destroy them
  for (var i = 0; i < charts.length; i++) {
    charts[i].destroy();
  }
  charts = [];

  // Get all elements with class 'ex-graph'
  var chartElements = document.getElementsByClassName("ex-graph");

  // Loop through all chart elements
  for (var i = 0; i < chartElements.length; i++) { // eslint-disable-line no-redeclare
    var chartElement = chartElements[i];

    // Get chart type and data from data-* attributes
    var chartType = chartElement.getAttribute("data-chart");
    var chartData = JSON.parse(chartElement.getAttribute("data-dataset"));
    var chartOptions = JSON.parse(
      chartElement.getAttribute("data-dataset-options")
    );
    var chartLabels = JSON.parse(chartElement.getAttribute("data-labels"));

    // Create chart using Chart.js
    var ctx = chartElement.getContext("2d");
    const chart = new Chart(ctx, {
      type: chartType,
      data: {
        labels: chartLabels,
        datasets: [
          {
            data: chartData,
            backgroundColor: chartOptions.backgroundColor,
            borderColor: chartOptions.borderColor,
          },
        ],
      },
    });

    // Add the chart instance to the charts array
    charts.push(chart);
  }
}

// Call the renderCharts function to initialize and render the charts
renderCharts();

// Function to resize charts on window resize
window.addEventListener("resize", function () {
  // Call the renderCharts function to resize the charts
  renderCharts();
});
