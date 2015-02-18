
$('.add_entry').on('submit', function(event){
    event.preventDefault();
    add_post();
  });


function add_post() {
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
    $('.add_entry').trigger('reset');
    $('.add_entry').after(response);
}
