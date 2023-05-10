// Update the count on the webpage
function updateCount(count) {
  document.getElementById("count").innerHTML = count;
}

// Increment the count
function incrementCount() {
  fetch("/add", { method: "POST" })
    .then(response => response.text())
    .then(count => updateCount(count));
}

// Decrement the count
function decrementCount() {
  fetch("/sub", { method: "POST" })
    .then(response => response.text())
    .then(count => updateCount(count));
}



