function updateCaption() {
    fetch("/generate_caption", { method: "GET" })
        .then(response => response.text())
        .then(data => {document.getElementById("caption-paragraph").textContent = data;})
        .catch(err => console.error('Error:', err));
}

document.getElementById("generate-caption-btn")
    .addEventListener("click", function() { updateCaption(); });