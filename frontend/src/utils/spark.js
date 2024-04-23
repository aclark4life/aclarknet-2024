// Via ChatGPT
function createSparkline(containerId) {
  // Get the container element
  var container = document.getElementById(containerId);

  // Get the canvas element
  var canvas = container.querySelector("canvas");

  // Get the dataset and labels from data attributes
  var dataset = JSON.parse(canvas.getAttribute("data-dataset"));
  var labels = JSON.parse(canvas.getAttribute("data-labels"));

  // Get the width, height, and color from style attribute
  var width = parseInt(canvas.style.width, 10);
  var height = parseInt(canvas.style.height, 10);
  var color = canvas.style.color;

  // Get the 2d rendering context of the canvas
  var ctx = canvas.getContext("2d");

  // Calculate the scale for x and y axes
  var scaleX = width / (labels.length - 1);
  var scaleY = height / (Math.max(...dataset[0]) - Math.min(...dataset[0]));

  // Draw the sparkline
  ctx.beginPath();
  ctx.moveTo(0, height - (dataset[0][0] - Math.min(...dataset[0])) * scaleY);
  for (var i = 1; i < labels.length; i++) {
    ctx.lineTo(
      i * scaleX,
      height - (dataset[0][i] - Math.min(...dataset[0])) * scaleY
    );
  }
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();
}

try {
  createSparkline("sparkline1Container");
  createSparkline("sparkline2Container");
  createSparkline("sparkline3Container");
} catch {
  console.log("error");
}
try {
  createSparkline("sparkline4Container");
  createSparkline("sparkline5Container");
  createSparkline("sparkline6Container");
  createSparkline("sparkline7Container");
} catch {
  console.log("error");
}
