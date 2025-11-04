// theme.js - place in frontend/
(function(){
  // toggle theme saved in localStorage
  const root = document.documentElement;
  const body = document.body;
  const saved = localStorage.getItem("smetic-theme");
  if(saved === "dark") body.classList.add("dark");

  window.toggleTheme = function toggleTheme(btn){
    if(body.classList.toggle("dark")){
      localStorage.setItem("smetic-theme","dark");
      btn.textContent = "☀️";
    } else {
      localStorage.setItem("smetic-theme","light");
      btn.textContent = "🌙";
    }
  };

  // password show/hide helper
  window.togglePassword = function togglePassword(id, btn){
    const el = document.getElementById(id);
    if(!el) return;
    if(el.type === "password"){ el.type = "text"; btn.textContent = "Hide"; }
    else { el.type = "password"; btn.textContent = "Show"; }
  };
})();
