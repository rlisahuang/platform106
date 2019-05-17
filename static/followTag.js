$("#tags-list").on("click", "label.follow-tag", function (event) {
    event.preventDefault();
    var followed = $(event.target).closest("form").find("input[name='followed']").val();
    console.log("follow: " + followed);
    var tid = $(event.target).closest("form").find("input[name='tid']").val();
    var button = $(this).find("input[name=follow-tag]");
    sendFollow(tid,followed,button);
});

function sendFollow(tid,followed,button) {
    console.log("Sending "+tid +" and " + followed +" to the back end");
    $.post(follow_URL,{'error':false, 'tid': tid, 'followed': followed},
    function(data,status){
        updateFollow(data,button);
    },'json');
}

function updateFollow(obj,button) {
    console.log(obj);
    if(obj.error) {
        // $("#errors").empty().html('Error: '+obj.err);
        alert(obj.err);
    } else {
        console.log("changing follow status to be " + obj.followed)
        if (obj.followed == "1") {
            button.val('Followed -- Click to unfollow');
        } else {
            button.val('Follow the Tag');
        }
        button.closest("form").find("input[name=followed]").val(obj.followed);
        button.closest("[data-tid]").find(".num_followers").text(obj.numFollows);
    }
}