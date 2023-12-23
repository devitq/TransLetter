function updatePaginationClass() {
    var paginationElement = document.querySelector('.pagination');

    if (window.innerWidth < 576) {
        paginationElement.classList.add('pagination-sm');
    } else {
        paginationElement.classList.remove('pagination-sm');
    }
}

updatePaginationClass();

window.addEventListener('resize', function() {
    updatePaginationClass();
});
