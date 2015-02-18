
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
      dataType: 'json',
      data: {'title': title, 'text': text},
      success: success
    });
}

function success(entry){
    $('.add_entry').trigger('reset');
    var template = '<article class="entry" id="entry{{id}}">'+
                      '<h3><a href= "/detail/{{id}}"><h3>{{title}}</a></h3>'+
                      '<p class="dateline">{{created}}'+
                      '<div class="entry_body">{{text}}</div>'+
                    '</article>';

    var html = Mustache.to_html(template, entry);
    $('.add_entry').after(html);
}
