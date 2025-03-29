const searchBox = document.getElementById("searchBox");
const suggestionsList = document.getElementById("suggestions");

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
      // TODO: Trigger recommendations and graph
    });
    suggestionsList.appendChild(li);
  });
});