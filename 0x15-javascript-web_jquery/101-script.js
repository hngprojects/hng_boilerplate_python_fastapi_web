$(document).ready(function(){
    $('#add_item').click(function(){
        $('ul.my_list').append('<li>Item</li>');
    });

    $('#remove_item').click(function(){
        $('ul.my_list li:last-child').remove();
    });

    $('#clear_list').click(function(){
        $('ul.my_list').empty();
    });
});
