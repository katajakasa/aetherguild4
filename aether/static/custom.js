$(document).ready(function() {
    $('.bbcode_field').sceditor({
        format: 'bbcode',
        style: '/static/sceditor/themes/content/custom.min.css',
        plugins: 'plaintext',
        emoticonsEnabled: false,
        autoUpdate: true,
        bbcodeTrim: true,
        width: '100%',
        height: '500px',
        toolbar: 'bold,italic,underline,strike|color,removeformat|cut,paste,pastetext|bulletlist,orderedlist|code,quote|image,link,unlink,youtube|date,time|print,maximize,source'
    });
    $('.fl-image').featherlight();
    $(".quote-post-link").click(function(){
        $.getJSON("/api/v1/posts/" + $(this).data('id'), function(data) {
            $('.bbcode_field').sceditor('instance').insertText('[quote='+data.user.profile.alias+']\n'+data.message+'\n[/quote]');
        });
    });
});