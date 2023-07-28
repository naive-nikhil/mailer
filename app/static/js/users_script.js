function togglePasswordVisibility(fieldNumber) {
  const passwordField = document.getElementById(`password-field-${fieldNumber}`);
  const passwordToggle = document.querySelector(`#password-field-${fieldNumber} + .password-toggle`);

  if (passwordField.type === 'password') {
    passwordField.type = 'text';
    passwordToggle.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
  } else {
    passwordField.type = 'password';
    passwordToggle.innerHTML = '<i class="fa-solid fa-eye"></i>';
  }
}

const passwordFields = document.querySelectorAll('input[type="password"]');
const passwordToggles = document.querySelectorAll('.password-toggle');

passwordFields.forEach(function (passwordField, index) {
  const passwordToggle = passwordToggles[index];

  passwordField.addEventListener('focus', function () {
    passwordToggle.classList.add('show');
  });

  passwordField.addEventListener('blur', function () {
    if (!passwordToggle.contains(document.activeElement)) {
      passwordToggle.classList.remove('show');
    }
  });

  passwordToggle.addEventListener('mousedown', function (event) {
    event.preventDefault();
    togglePasswordVisibility(index + 1);
  });
});
