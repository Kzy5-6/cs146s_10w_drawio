const API_BASE = "http://127.0.0.1:8000";
const form = document.querySelector("#note-form");
const status = document.querySelector("#status");
const notesList = document.querySelector("#notes");

async function loadNotes() {
  // TODO: Fetch GET /notes, handle errors, and render notes with safe DOM APIs.
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: document.querySelector("#title").value,
    body: document.querySelector("#body").value,
  };

  // TODO: Send POST /notes, show success/failure state, then refresh the list.
});

loadNotes();
