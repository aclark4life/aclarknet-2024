var draggableElements = document.getElementsByClassName('draggable');
var offsetX, offsetY;
var isDragging = false;
var currentDragElement;

for (var i = 0; i < draggableElements.length; i++) {
  var draggableElement = draggableElements[i];
  draggableElement.addEventListener('mousedown', dragStart);
  document.addEventListener('mousemove', drag);
  document.addEventListener('mouseup', dragEnd);
}

function dragStart(event) {
  isDragging = true;
  offsetX = event.clientX - this.offsetLeft;
  offsetY = event.clientY - this.offsetTop;
  currentDragElement = this;
}

function drag(event) {
  if (isDragging && currentDragElement) {
    event.preventDefault();
    currentDragElement.style.left = (event.clientX - offsetX) + 'px';
    currentDragElement.style.top = (event.clientY - offsetY) + 'px';

    var x = event.clientX - offsetX;
    var y = event.clientY - offsetY;
    console.log('X:', x, 'Y:', y);
  }
}

function dragEnd() {
  isDragging = false;
  currentDragElement = null;

  // Get all draggable elements and their positions
  var draggableElements = document.getElementsByClassName('draggable');
  var draggablePositions = {};

  for (var i = 0; i < draggableElements.length; i++) {
    var draggableElement = draggableElements[i];
    var id = draggableElement.id;
    var left = draggableElement.style.left;
    var top = draggableElement.style.top;
    draggablePositions[id] = { left: left, top: top };
  }

  // Convert the positions to JSON string
  var positionsJSON = JSON.stringify(draggablePositions);

  // Send the positions data to your Django server to save it in the Profile object
  // You can use AJAX or any other method to send the data to your Django server endpoint
  // Example AJAX call:
  var csrfToken = getCookie('csrfmiddlewaretoken');
  var request = new XMLHttpRequest();
  request.open('POST', '/save_positions/', true);
  request.setRequestHeader('Content-Type', 'application/json');
  request.setRequestHeader('X-CSRFToken', csrfToken);
  request.send(positionsJSON);
}

// Retrieve the CSRF token from the cookie
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Check if the cookie name matches the expected CSRF cookie name
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
