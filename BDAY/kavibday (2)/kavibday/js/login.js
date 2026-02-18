function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const correctUsername = "SKAVISRI";
  const correctPassword = "Kavisss";

  if (username === correctUsername && password === correctPassword) {
    localStorage.setItem("bday_auth", "1");
    window.location.href = "home.html";
  } else {
    document.getElementById("error").innerText =
      "Oops... think about how we say it.";
  }
}
