const themeToggle = document.getElementById("theme-toggle");

themeToggle?.addEventListener("click", () => {
  document.body.classList.toggle("light-mode");
  if (document.body.classList.contains("light-mode")) {
    document.body.style.background = "var(--bg-light)";
    document.body.style.color = "var(--text-light)";
  } else {
    document.body.style.background = "var(--bg-dark)";
    document.body.style.color = "var(--text-dark)";
  }
});
