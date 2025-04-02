const searchBox = document.getElementById("searchBox");
const suggestionsList = document.getElementById("suggestions");
const recommendationGrid = document.getElementById("recommendationGrid");

// 🔍 Handle input in the search box
searchBox.addEventListener("input", async (e) => {
  const query = e.target.value;
  if (query.length < 2) {
    suggestionsList.innerHTML = "";
    return;
  }

  const res = await fetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });

  const results = await res.json();

  suggestionsList.innerHTML = "";
  results.forEach((book) => {
    const li = document.createElement("li");
    li.textContent = book.title;
    li.addEventListener("click", () => {
      searchBox.value = book.title;
      suggestionsList.innerHTML = "";
      loadRecommendations(book.isbn); // 🧠 Trigger the recommendation
    });
    suggestionsList.appendChild(li);
  });
});

// 📚 Load book recommendations for selected ISBN
function loadRecommendations(isbn) {
  fetch(`/predict/${isbn}`)
    .then(response => response.json())
    .then(data => {
      recommendationGrid.innerHTML = "";

      if (data.length === 0) {
        recommendationGrid.innerHTML = "<p>No recommendations found.</p>";
        return;
      }

      data.forEach(book => {
        const card = `
          <div class="book-card">
            <h3>${book.title}</h3>
            <p><strong>Author:</strong> ${book.author}</p>
            <p><strong>Similarity:</strong> ${book.similarity.replace("_", " ")}</p>
            <p><strong>Year:</strong> ${book.year || "Unknown"}</p>
          </div>
        `;
        recommendationGrid.innerHTML += card;
      });
    })
    .catch(err => {
      console.error("Error fetching recommendations:", err);
      recommendationGrid.innerHTML = "<p>❌ Failed to load recommendations.</p>";
    });
}