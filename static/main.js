$(document).ready(function () {
  $('.add_entry').on('submit', function(event){
      event.preventDefault();
      add_post();
    });
  $('#editLink').on("click", function(event){
      event.preventDefault();
      open_edit();
    });
})




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

function open_edit() {
    var id = $('.entry').attr('id').split("entry")[1];
    $.ajax({
      url: '/editview',
      type: 'GET',
      dataType: 'json',
      data: {'id': id},
      success: open_edit_success,
      error: open_edit_fail
    });
}

function success(entry){
    $('.add_entry').trigger('reset');
    var template = '<article class="entry" id="entry{{id}}">'+
                      '<h3><a href= "/detail/{{id}}"><h3>{{title}}</a></h3>'+
                      '<p class="dateline">{{created}}'+
                      '<div class="entry_body">{{{text}}}</div>'+
                    '</article>';

    var html = Mustache.to_html(template, entry);
    $('.add_entry').after(html);
}


function open_edit_success(entry){
  console.log("success")
  var template = '<aside><form action="{{ request.route_url("editview", id=entry.id) }}" method="POST" class="edit_entry">'+
                 '<div class="field"><label for="title">Title</label>'+
                 '<input type="text" value="{{title}}" size="30" name="title" id="title"/></div>'+
                 '<div class="field"><label for="text">Text</label>'+
                 '<textarea name="text" id="text" rows="5" cols="80">{{text}}</textarea></div>'+
                 '<div class="control_row"><input type="submit" value="Share" name="Share"/></div></form></aside>';

  var html = Mustache.to_html(template, entry);
  $('#content').html(html);
}



function open_edit_fail(entry){
  console.log("fail");
  console.log(entry);
}




