if (localStorage.getItem("bday_auth") !== "1") {
  window.location.href = "index.html";
}

function goTo(page) {
  window.location.href = page;
}
