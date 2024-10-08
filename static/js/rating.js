// Получаем все элементы звезд
const stars = document.querySelectorAll('.star');
const ratingInput = document.querySelector('#rating-value');
let currentRating = 0;

// Функция для установки рейтинга по клику
function setRating(rating) {
    resetStars();
    for (let i = 0; i < rating; i++) {
        stars[i].classList.add('selected');
    }
    currentRating = rating;
    ratingInput.value = rating;
}

// Сброс всех звезд
function resetStars() {
    stars.forEach(star => {
        star.classList.remove('selected');
    });
}

// Добавление обработчиков событий на звезды
stars.forEach((star, index) => {
    // Наведение мыши на звезды
    star.addEventListener('mouseover', () => {
        resetStars();
        for (let i = 0; i <= index; i++) {
            stars[i].classList.add('hover');
        }
    });

    // Убираем выделение при выходе мыши
    star.addEventListener('mouseout', () => {
        stars.forEach(s => s.classList.remove('hover')); // Удаляем hover у всех звезд
        setRating(currentRating); // Восстанавливаем текущее выбранное количество звезд
    });

    // Выбор звезд при клике
    star.addEventListener('click', () => {
        setRating(index + 1);
    });
});
