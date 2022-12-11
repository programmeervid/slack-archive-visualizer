function search() {
    var keywords = document.getElementById("searchbar-textfield").value;
    for (const x of document.getElementsByClassName("result-container")) {
        var regex = new RegExp('<span class="highlight">([^<>\n]*)<\/span>', 'ig');
        x.querySelector(".message").querySelector(".msg-hidden").querySelector("p").innerHTML = x.querySelector(".message").querySelector(".msg-hidden").querySelector("p").innerHTML.replace(regex, '$1');
        var content = x.querySelector(".message").querySelector(".msg-hidden").querySelector("p").innerHTML;
        var firstIndex = content.toLowerCase().indexOf(keywords.toLowerCase());
        if (firstIndex == -1) {
            x.hidden = true;
        } else {
            x.hidden = false;
            var offset = Math.max(0, Math.min(firstIndex, firstIndex+keywords.length-32));
            var prefix = "";
            if (offset > 0) {
                prefix = "...";
            } else {
                prefix = "";
            }
            x.querySelector(".message").querySelector(".msg").querySelector("p").innerHTML = prefix + content.slice(offset, firstIndex) + "<span class='highlight'>" + content.slice(firstIndex, firstIndex+keywords.length) + "</span>" + content.slice(firstIndex+keywords.length, content.length);
        }
    }
}