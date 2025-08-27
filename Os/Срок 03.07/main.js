const form = document.getElementById("form");

function emailValidation(email){
    let valid = true;
    let emailExcept = document.getElementById('emailExcept');
    emailExcept.textContent = "";
    emailExcept.style.display = 'none';
    let dom_start_index = email.indexOf("@")+1;
    let size = email.length;
    if (
        size - dom_start_index <= 2
        ||
        email.slice(dom_start_index, size-1).indexOf(".") == -1
    ){
        valid = false;
        emailExcept.textContent = "Exception at email! Wrong format or data";
        emailExcept.style.display = 'block';
    }
    return valid;
}

function passwordValidation(password, password_){
    let valid = true;
    let passwordExcept = document.getElementById('passwordExcept');
    passwordExcept.textContent = "";
    passwordExcept.style.display = 'none';
    if (
        password !== password_
        ||
        password <= 5
        ||
        /\d/.test(password) == false
        ||
        /[A-Z]/.test(password) == false
        ||
        /[a-z]/.test(password) == false
    ){
        passwordExcept.textContent = "Exception at password! Wrong format or data";
        passwordExcept.style.display = 'block';
        valid = false;
    }
    return valid;
}

form.addEventListener('submit', function (event){
    event.preventDefault();
    const formData = new FormData(form);
    const email = formData.get('mail');
    const password = formData.get('pass');
    const password_ = formData.get('pass_');
    let eVal = emailValidation(email);
    let pVal = passwordValidation(password, password_);
    if (eVal && pVal){
        window.location = "./user.html";
    }
})