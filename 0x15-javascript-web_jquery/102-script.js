$(document).ready(function(){
    $('#btn_translate').click(function(){
        var languageCode = $('#language_code').val();
        $.get('https://www.fourtonfish.com/hellosalut/hello/', {lang: languageCode}, function(data){
            $('#hello').text(data.hello);
        });
    });
});
