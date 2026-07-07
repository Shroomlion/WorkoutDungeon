// When a set row's exercise changes, show only the fields its measurement
// type uses. Pure UX — server-side form validation remains the enforcement.

const FIELD_MAP = JSON.parse(document.getElementById("field-map").textContent);

const MEASURED = ["reps", "weight_kg", "duration_seconds", "distance_m"];

function updateRow(select) {
    const row = select.closest(".set-row");
    // Before an exercise is chosen, `wanted` is undefined -> hide all
    // measured fields; an untouched row is just its dropdown.
    const wanted = FIELD_MAP[select.value];
    for (const name of MEASURED) {
        const input = row.querySelector(`[name$="-${name}"]`);
        input.closest(".field").hidden = !wanted || !wanted.includes(name);
    }
}

document.addEventListener("change", (event) => {
    if (event.target.matches('select[name$="-exercise"]')) {
        updateRow(event.target);
    }
});

// Initial pass: rows can arrive pre-filled, e.g. when the form re-renders
// with validation errors.
for (const select of document.querySelectorAll('select[name$="-exercise"]')) {
    updateRow(select);
}
