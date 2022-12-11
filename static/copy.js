function msgCopy() {
    window.getSelection().removeAllRanges();
    let range = document.createRange();
    range.selectNode(rightClickedElem.querySelector(".message").querySelector(".msg"));
    window.getSelection().addRange(range);
    document.execCommand('copy');
    window.getSelection().removeAllRanges();
}

function msgCopyPlain() {
    navigator.clipboard.writeText(rightClickedElem.querySelector(".message").querySelector(".msg").textContent.trim()).then(function() {}, function(err) {});
}
