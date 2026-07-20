document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const errorBox = document.getElementById("auth-error");

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
  }

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.classList.add("hidden");
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    try {
      const { token, user } = await Api.login(email, password);
      setToken(token);
      setStoredUser(user);
      window.location.href = "index.html";
    } catch (err) {
      showError(err.message);
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.classList.add("hidden");
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const nickname = document.getElementById("register-nickname").value;
    try {
      const { token, user } = await Api.register(email, password, nickname);
      setToken(token);
      setStoredUser(user);
      window.location.href = "index.html";
    } catch (err) {
      showError(err.message);
    }
  });
});
