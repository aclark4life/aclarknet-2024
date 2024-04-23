import bootstrap from "bootstrap/dist/js/bootstrap.bundle";

// Assuming you have a button or element that triggers the modal with the data target "fakeTextModal"
const modalTrigger = document.querySelector(
  "[data-bs-target='#fakeTextModal']"
);

var previousNavLink;
var loremNavLink;

// Function to handle the HTTP request and display the results in the modal
function makeHttpRequestAndOpenModal() {
  fetch("/dashboard/fake-text/")
    .then((response) => response.json())
    .then((data) => {
      // Create an HTML element to display the results
      const resultElement = document.createElement("p");
      resultElement.textContent = data["paragraph"]; // Only display the first element of the array

      // Clear the existing content of the modal body
      const modalBody = document.querySelector("#fakeTextModal .modal-body");
      modalBody.innerHTML = "";

      // Append the result element to the modal body
      modalBody.appendChild(resultElement);

      // Open the modal
      const fakeTextModal = new bootstrap.Modal(
        document.getElementById("fakeTextModal")
      );
      fakeTextModal.show();
    })
    .catch((error) => {
      console.error(error);
    });

  var navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach(function (item) {
    if (item.classList.contains("active")) {
      item.classList.remove("active");
      previousNavLink = item;
    }
  });
  this.classList.add("active");
  loremNavLink = this;
}

// Add an event listener to the modal trigger button
modalTrigger.addEventListener("click", makeHttpRequestAndOpenModal);

// Remove the darkened overlay when the modal is hidden
const fakeTextModal = document.getElementById("fakeTextModal");
fakeTextModal.addEventListener("hidden.bs.modal", () => {
  const modalBackdrop = document.querySelector(".modal-backdrop");
  modalBackdrop.parentNode.removeChild(modalBackdrop);
  previousNavLink.classList.add("active");
  loremNavLink.classList.remove("active");
});
