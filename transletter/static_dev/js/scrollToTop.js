document.addEventListener('DOMContentLoaded', function() {
    window.onscroll = function() {
        var scrollHeight = window.innerHeight;
        var topElement = document.getElementById('ScrollToTop');
        var yOffset = window.pageYOffset;

        if (yOffset > scrollHeight) {
            topElement.classList.add('active');
        } else {
            topElement.classList.remove('active');
        }
    };
});