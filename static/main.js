function add_post() {
    console.log("test add post");
    var title = $('#title').val();
    var text = $('#text').val();
    $.ajax({
      url: '/add',
      type: 'POST',
      dataType: 'html',
      data: {'title': title, 'text': text},
      success: success
    });
}

function success(response){
    $(".add_entry").after(response)
}