function add_post() {
    console.log("test add post")
    var title = $('input#title').val();
    var text = $('textarea#text').val();
    var data = {'title': title, 'text': text};
    $.post("/add", data)
        .done(function(){$.get("/home");
    });
      
}