document.addEventListener("DOMContentLoaded", function() {
  console.log("activo");
  // Tu código JavaScript aquí
});


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
      document.getElementById("login").classList.toggle("active");
      document.getElementById("uno").classList.toggle("active");
      document.getElementById("dos").classList.toggle("active");
      document.getElementById("tres").classList.toggle("active");
      document.getElementById("cuatro").classList.toggle("active");
      document.getElementById("cinco").classList.toggle("active");
  });
});


//General
const spaceHolder = document.querySelector('.space-holder');
const horizontal = document.querySelector('.horizontal');
spaceHolder.style.height = `${calcDynamicHeight(horizontal)}px`;

function calcDynamicHeight(ref) {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const objectWidth = ref.scrollWidth;
  return objectWidth - vw + vh + 150; // 150 is the padding (in pixels) desired on the right side of the .cards container. This can be set to whatever your styles dictate
}

window.addEventListener('scroll', () => {
  const sticky = document.querySelector('.sticky');
  const horizontal = document.querySelector('.horizontal');
  horizontal.style.transform = `translateX(-${window.scrollY}px)`;
});

window.addEventListener('resize', () => {
  spaceHolder.style.height = `${calcDynamicHeight(horizontal)}px`;
});


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








//JSON
// const idioma_cast = './JSON/JSON.json'
// const idioma_en = './JSON/JSON_Eng.json'

// const error_cast = "Error al cargar el archivo JSON"
// const error_en = "Error to load the JSON file"
// json_cast();

// function idiomas(idioma, error_msg) {


//     // Función para cambiar el idioma a español
//     fetch(idioma)
//         .then(response => response.json())
//         .then(data => {
//             console.log("Entra")
//             const login = data.login
// 			const header = data.header

// 			const .... = document.getElementById("....")
// 		})
//         .catch(error => console.error(error_msg, error))
// };

// function json_cast(){
//     idiomas(idioma_cast, error_cast)
// }
// function json_en(){
//     idiomas(idioma_en, error_en)
// }