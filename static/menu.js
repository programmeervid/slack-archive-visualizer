function getHierarchy(elem) {
    var hierarchy = [elem];
    while(elem.parentNode && elem.parentNode.nodeName.toLowerCase() != 'body') {
        elem = elem.parentNode;
        hierarchy.push(elem);
    }
    return hierarchy;
}

function hideMenu() {
    document.getElementById(
        "contextMenu").style.display = "none"
}

function rightClick(e, elem) {
    e.preventDefault();
    console.log(elem)
    rightClickedElem = elem;

    if (document.getElementById(
        "contextMenu").style.display == "block")
        hideMenu();
    else {
        var menu = document
            .getElementById("contextMenu")
                
        menu.style.display = 'block';
        menu.style.left = e.pageX-5 + "px";
        menu.style.top = e.pageY-10 + "px";
    }
}