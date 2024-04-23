// Select all image links with data-bs-toggle="modal"
const imageLinks = document.querySelectorAll('[data-bs-toggle="modal"]');

// Select the modal's image element
const modalImage = document.getElementById('modalImage');

// Iterate over each image link and attach a click event listener
imageLinks.forEach(link => {
   link.addEventListener('shown.bs.modal', function () {
      // Get the source URL of the clicked image
      const imageUrl = this.querySelector('img').src;
      
      // Set the source URL for the modal's image element
      modalImage.src = imageUrl;
   });
});
