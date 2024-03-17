document.addEventListener('DOMContentLoaded', function() {
    feather.replace();
    const eye = document.querySelector(".feather-eye");
    const eyeoff = document.querySelector(".feather-eye-off");
    const password = document.querySelector("input[type=password]");

    eye.addEventListener("click", function() {
        eye.style.display = "none";
        eyeoff.style.display = "block";
        password.type = "text";
    });

    eyeoff.addEventListener("click", function() {
        eye.style.display = "block";
        eyeoff.style.display = "none";
        password.type = "password";
    });
});
