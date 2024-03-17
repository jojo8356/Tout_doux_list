document.querySelector(".checkbox").addEventListener('click', function() {
    var checkbox = this;
    var checkboxInput = document.querySelector(".input-checkbox");
    
    checkbox.classList.toggle("checkbox-off");
    checkbox.classList.toggle("checkbox-on");
    checkbox.innerHTML = checkbox.classList.contains("checkbox-off") ? "" : "&#10004";
    checkboxInput.value = checkbox.classList.contains("checkbox-off") ? "false" : "true";
});
