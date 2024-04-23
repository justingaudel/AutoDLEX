
$(document).ready(function(){
        $("#profile_image").change(function(){
            if (this.files.length > 0) {
                var imageFileType = this.files[0].type;
                var match = ["image/jpeg", "image/png", "image/gif", "image/jpg"];
    
                if (!(match.includes(imageFileType))) {
                    swal({
                        title: "Invalid Image File",
                        text: "Please select a valid image file (JPEG/PNG/GIF/JPG)",
                        icon: "error",
                        button: "OK"
                    }).then(function() {
                        $('#profile_image').val('');
                    });
                    return false;
                }
            }
        });
    });

