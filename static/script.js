$(document).ready(function () {
    $('#search-box').on('input', function () {
        let query = $(this).val();
        $.ajax({
            url: "/search",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ query: query }),
            success: function (data) {
                let results = $('#results');
                results.empty();
                data.forEach(book => {
                    results.append(`<li>${book.title} (Rating: ${book.rating})</li>`);
                });
            }
        });
    });
});