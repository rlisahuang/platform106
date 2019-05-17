$("#posts-list").on("click", "label.star-event", function (event) {
    event.preventDefault();
    var starred = $(event.target).closest("form").find("input[name='starred']").val();
    var pid = $(event.target).closest("form").find("input[name='pid']").val();
    var button = $(this).find("input[name=star-event]");
    sendStar(pid,starred,button);
});

function sendStar(pid,starred,button) {
    console.log("Sending "+pid +" and " + starred +" to the back end");
    $.post(star_URL,{'error':false, 'pid': pid, 'starred': starred},
    function(data,status){
        updateStar(data,button);
    },'json');
}

function updateStar(obj,button) {
    console.log(obj);
    if(obj.error) {
        alert(obj.err);
    } else {
        console.log("changing star status to be " + obj.starred)
        if (obj.starred == "1") {
            button.val('Starred -- Click to unstar');
        } else {
            button.val('Star the Event');
        }
        button.closest("form").find("input[name=starred]").val(obj.starred);
    }
}