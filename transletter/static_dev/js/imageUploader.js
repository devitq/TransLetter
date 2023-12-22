document.addEventListener('DOMContentLoaded', function () {
    
    var readURL = function (input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                document.querySelector('.profile-pic').setAttribute('src', e.target.result);
            };

            reader.readAsDataURL(input.files[0]);
        }
    };

    document.querySelector(".file-upload").addEventListener('change', function () {
        readURL(this);
    });

    document.querySelector(".upload-button").addEventListener('click', function () {
        document.querySelector(".file-upload").click();
    });
});