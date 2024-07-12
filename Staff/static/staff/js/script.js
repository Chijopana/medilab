// scroll
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // Esta opción permite que el scroll sea suave
    });
  }
  function scrollToPosition(position) {
    window.scrollTo({
        top: position,
        behavior: 'smooth'
    });
  } function scrollToBottom() {
    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
    });
  }


  // Darkmode
document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.slider');
    const checkbox = document.querySelector('.box');
    slider.addEventListener('click', () => {
        checkbox.checked = !checkbox.checked;
        slider.classList.toggle("active");
        document.body.classList.toggle("active");
        document.getElementById("bumper_2").classList.toggle("active");
        document.getElementById("texto").classList.toggle("active");
    });
  });

  //lista pacientes

  