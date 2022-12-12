from os import getcwd, listdir, mkdir, remove
from os.path import join, isdir, isfile, basename, splitext
from functools import reduce
import re
import json
from tkinter import E
import urllib.request
import datetime
import easygui

def parse_emoji_code(code, alt="", emojis={}):
    # looks up HTML encoding for the given emoji using the given emojis dictionary
    res = emojis.get(code, "")
    if not res:
        print("WARNING: unknown emoji code \"" + code + "\"")
    return "".join(list(map(lambda y: (r"&#x" + y + r";") if y else alt.replace("_", "&#95;"), res.split("-"))))

def escape_markup_chars(string, escape_url_chars=False):
    # removes markup characters from the given string
    if escape_url_chars:
        return string.replace(r"_", r"&#95;").replace(r"~", r"&#126;").replace(r"*", r"&#42").replace(r".", r"&#46;").replace(r"&gt;", r"&#62;")
    else:
        return string.replace(r"_", r"&#95;").replace(r"~", r"&#126;").replace(r"*", r"&#42")

def get_list_style_type(marker, level):
    # determines the style of the list based on the marker and the level (indentation)
    if re.match(r"[0-9a-zA-Z]", marker):
        if level in [0, 3]:
            return r"style='list-style-type: decimal;'"
        elif level in [1, 4]:
            return r"style='list-style-type: lower-latin;'"
        elif level in [2]:
            return r"style='list-style-type: lower-roman;'"
        else:
            return r""
    elif re.match(r"[•◦▪]", marker):
        if level in [0, 3]:
            return r"style='list-style-type: disc;' class='bullet'"
        elif level in [1, 4]:
            return r"style='list-style-type: circle;' class='bullet'"
        elif level in [2]:
            return r"style='list-style-type: square;' class='bullet'"
        else:
            return r""
    else:
        return r""

def get_html_list(text):
    # converts text to HTML list segment, where each line in the text is a separate <li> element
    lines = text.split("\n")
    indentations = list(map(lambda x: int(x.find(re.search(r" *(.*)", x).group(1))/4), text.split("\n")))
    content = r"</p><ul class=message-list-outer>"
    for i in range(len(lines)):
        if indentations[i] > indentations[max(i-1, 0)]:
            content += r"<ul class=message-list>"*(indentations[i]-indentations[max(i-1, 0)])
        content += r"<li " + get_list_style_type(lines[i].strip()[0], indentations[i]) + r">" + lines[i][2+indentations[i]*4:] + r"</li>"
        if indentations[i] > indentations[min(i+1, len(lines)-1)]:
            content += r"</ul>"*(indentations[i]-indentations[min(i+1, len(lines)-1)])
    content += r"</ul><p>"
    return content

def parse_markup(text, users, channel_names, emojis={}):
    # converts source text to HTML text by interpreting markdown, emojis and references like @'s and #'s
    text = re.sub(r"(:([a-z_\+\-][a-z0-9_\+\-]*):)", lambda x: parse_emoji_code(x.group(2), alt=x.group(1), emojis=emojis), text)
    text = re.sub(r"<@([a-zA-Z0-9]*)>", lambda x: escape_markup_chars(r"<b class=reference-personal>@"+users.get(x.group(1), {}).get("name", "")+r"</b>"), text)
    text = re.sub(r"<#([a-zA-Z0-9]*)[|]([^<|>:/]*)>", lambda x: escape_markup_chars(r"<a href=" + x.group(2) + r".html><b class=reference-message>#" + x.group(2) + r"</b></a>", escape_url_chars=True), text)
    text = re.sub(r"<([^<>\n/]*)://([^<>\n/]*)\.slack\.com/archives/([a-zA-Z0-9]*)/p([0-9]*)(\?thread_ts=([0-9.]*)&amp;cid=([a-zA-Z0-9]*))?(\|([^<>\n/]*)://([^<>\n/]*)\.slack\.com/archives/([a-zA-Z0-9]*)/p([0-9]*))?>", lambda x: escape_markup_chars(r"<a href="+channel_names.get(x.group(3), "")+".html#"+x.group(4)+"><b class=reference-message># "+channel_names.get(x.group(3), "")+" / "+x.group(4)+r"</b></a>", escape_url_chars=True), text)
    text = re.sub(r"<([^<|>]*)[|]([^<|>]*)>", lambda x: escape_markup_chars(r"<a href=" + x.group(1) + r">" + x.group(2) + r"</a>", escape_url_chars=True), text)
    text = re.sub(r"<(http[^<>\n]*youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})[^<>\n]*)>", lambda x: escape_markup_chars(r"<a href=" + x.group(1) + r">" + x.group(1) + r"</a><div class=yt-embed><iframe src=https://www.youtube.com/embed/" + x.group(2) + r" frameborder=0 allow=encrypted-media; allowfullscreen></iframe></div>", escape_url_chars=True), text)
    text = re.sub(r"<(http[^<>\n]*youtu\.be/([a-zA-Z0-9_-]{11})[^<>\n]*)>", lambda x: escape_markup_chars(r"<a href=" + x.group(1) + r">" + x.group(1) + r"</a><div class=yt-embed><iframe src=https://www.youtube.com/embed/" + x.group(2) + r" frameborder=0 allow=encrypted-media; allowfullscreen></iframe></div>", escape_url_chars=True), text)
    text = re.sub(r"<(http[^<>\n]*)>", lambda x: escape_markup_chars(r"<a href=" + x.group(1) + r">" + x.group(1) + r"</a>", escape_url_chars=True), text)
    text = re.sub(r"```([^`]*)```", lambda x: escape_markup_chars(r"</p><pre><code>" + x.group(1) + r"</code></pre><p>", escape_url_chars=True), text)
    text = re.sub(r"`([^`]*)`", lambda x: escape_markup_chars(r"<code>" + x.group(1) + r"</code>", escape_url_chars=True), text)
    text = re.sub(r"(?<!.)( *(?:[•◦▪]|[0-9]{1,3}\.|[a-z]{1,2}\.|[ivx]{1,4}\.).*(?:\n *(?:[•◦▪]|[0-9]{1,3}\.|[a-z]{1,2}\.|[ivx]{1,4}\.).*)*)", lambda x: get_html_list(x.group(1)), text)
    text = re.sub(r"(&gt; .*(\n&gt; .*)*)", lambda x: r"</p><blockquote><p>" + x.group(1).replace("&gt; ", "") + r"</p></blockquote><p>", text)
    text = re.sub(r"(</blockquote><p>)\n", r"\1", text)
    text = re.sub(r"\n*(</p>)", r"\1", text)
    text = re.sub(r"\*((?:[^\*](?!<li>)(?!</li>)(?!<ul>)(?!</ul>)(?!<code>)(?!</code>)(?!<blockquote>)(?!</blockquote>))*)\*", r"<strong>\1</strong>", text)
    text = re.sub(r"_((?:[^_](?!<li>)(?!</li>)(?!<ul>)(?!</ul>)(?!<code>)(?!</code>)(?!<blockquote>)(?!</blockquote>))*)_", r"<em>\1</em>", text)
    text = re.sub(r"~((?:[^~](?!<li>)(?!</li>)(?!<ul>)(?!</ul>)(?!<code>)(?!</code>)(?!<blockquote>)(?!</blockquote>))*)~", r"<del>\1</del>", text)
    text = re.sub(r"\n(<ul)", r"\1", text)
    return text

def strip_markup(text, users, channel_names, emojis={}):
    # strips markup from text (for search on index page)
    text = re.sub(r"(:([a-z_\+\-][a-z0-9_\+\-]*):)", lambda x: parse_emoji_code(x.group(2), alt=x.group(1), emojis=emojis), text)
    text = re.sub(r"<@([a-zA-Z0-9]*)>", lambda x: escape_markup_chars(r"@"+users.get(x.group(1), {}).get("name", "")), text)
    text = re.sub(r"<#([a-zA-Z0-9]*)[|]([^<|>:/]*)>", lambda x: escape_markup_chars(r"#" + x.group(2)), text)
    text = re.sub(r"<([^<>\n/]*)://([^<>\n/]*)\.slack\.com/archives/([a-zA-Z0-9]*)/p([0-9]*)(\?thread_ts=([0-9.]*)&amp;cid=([a-zA-Z0-9]*))?(\|([^<>\n/]*)://([^<>\n/]*)\.slack\.com/archives/([a-zA-Z0-9]*)/p([0-9]*))?>", r"", text)
    text = re.sub(r"<([^<|>]*)[|]([^<|>]*)>", lambda x: escape_markup_chars(x.group(2) + r": " + x.group(1)), text)
    text = re.sub(r"<(http[^<>\n]*)>", lambda x: escape_markup_chars(x.group(1)), text)
    text = re.sub(r"(&gt; .*(\n&gt; .*)*)", lambda x: x.group(1).replace("&gt; ", ""), text)
    text = re.sub(r"```([^`]*)```", lambda x: escape_markup_chars(x.group(1)), text)
    text = re.sub(r"`([^`]*)`", lambda x: escape_markup_chars(x.group(1)), text)
    text = re.sub(r"\*([^\*]*)\*", r"\1", text)
    text = re.sub(r"_([^_]*)_", r"\1", text)
    text = re.sub(r"~([^~]*)~", r"\1", text)
    return text

def get_html_head(title, subtitle, is_index=False):
    # generates HTML head
    content = "<!DOCTYPE html>\n<html lang=\"en\">\n\t<head>\n\t\t<meta charset=\"utf-8\">\n\t\t<title>"
    content += subtitle + " - " + title
    content += "</title>\n\t\t<link rel=\"icon\" type=\"image/x-icon\" href=\""
    if not is_index:
        content += "../"
    content += "static/favicon.ico\">\n\t\t<link rel=stylesheet type=text/css href=\""
    if not is_index:
        content += "../"
    content += "static/style.css\">\n"
    if is_index:
        content += "\t\t<script src=\"static/search.js\"></script>\n"
    content += "\t\t<script src=\""
    if not is_index:
        content += "../"
    content += "static/menu.js\"></script>\n"
    if not is_index:
        content += "\t\t<script>\n\t\t\tfunction reloadHash() {\n\t\t\t\tif (window.location.hash) {\n\t\t\t\t\twindow.location.href = window.location.hash;\n\t\t\t\t}\n\t\t\t}\n\t\t</script>\n"
    content += "\t\t<script src=\""
    if not is_index:
        content += "../"
    content += "static/copy.js\"></script>\n\t\t<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css\">\n\t</head>\n"
    return content

def get_html_body(title, sidebar_content, messages_content, is_index=False):
    # generates HTML body
    if is_index:
        content = "\t<body>\n"
    else:
        content = "\t<body onload=\"reloadHash()\">\n"
    content += "\t\t<div id=\"slack-archive-viewer\">\n\t\t\t<div id=\"sidebar\">\n\t\t\t\t<a href=\""
    if not is_index:
        content += "../"
    content += "index.html\" style=\"text-decoration: none;\"><h3 id=\"channel-title\">"
    content += title
    content += "</h3></a>\n\t\t\t\t<ul class=\"list\" id=\"channel-list\">\n"
    content += sidebar_content
    content += "\n\t\t\t\t</ul>\n\t\t\t</div>\n\t\t\t<div class=\""
    content += "index-container" if is_index else "messages"
    content += "\">\n"
    content += messages_content
    content += "\n\t\t\t</div>\n\t\t</div>\n"
    content += "\t\t<script>\n"
    content += "\t\t\tvar rightClickedElem;\n"
    content += "\t\t\tdocument.addEventListener('contextmenu', e => {\n"
    content += "\t\t\t\tvar elems = Array.prototype.slice.call(document.querySelectorAll(\":hover\"));\n"
    content += "\t\t\t\tvar aIndex = elems.findLastIndex(element => element.tagName == \"A\");\n"
    content += "\t\t\t\tvar mIndex = elems.findLastIndex(element => element.classList.contains(\"message-container\"))\n"
    content += "\t\t\t\tif (mIndex >= 0 && mIndex > aIndex) {rightClick(e, elems[mIndex])}\n"
    content += "\t\t\t}, {passive: false})\n"
    content += "\t\t\tdocument.onclick = hideMenu;\n"
    content += "\t\t</script>\n"
    if is_index:
        content += "\t\t<script>\n\t\t\tdocument.getElementById(\"searchbar-textfield\").addEventListener(\"keyup\", function(event) {\n\t\t\t\tsearch();\n\t\t\t});\n\t\t</script>\n"
    content += "\t\t<div id=\"contextMenu\" class=\"context-menu\" style=\"display:none\">\n\t\t\t<ul>\n\t\t\t\t<li onclick=\"msgCopy()\">Copy</li>\n\t\t\t\t<li onclick=\"msgCopyPlain()\">Copy plain text</li>\n\t\t\t</ul>\n\t\t</div>"
    content += "\t</body>\n</html>"
    return content

def get_html_sidebar(channels, current_channel="", is_index=False):
    # generates HTML sidebar
    content = ""
    for c in channels:
        content += "\t\t\t\t\t<li class=\"channel"
        content += " active" if c == current_channel else ""
        content += "\">\n\t\t\t\t\t\t<a href=\""
        if is_index:
            content += "channels/"
        content += c
        content += ".html\">"
        content += c
        content += "</a>\n\t\t\t\t\t</li>\n"
    return content

def get_html_files(files):
    # generates HTML for shared files inside a message
    content = ""
    for f in files:
        name = mimetype = f.get("name", "")
        mimetype = f.get("mimetype", "")
        url = f.get("url_private_download", "")
        if "image" in mimetype:
            content += "\t\t\t\t\t<div class=\"message-image\">\n\t\t\t\t\t\t<a href=\"../"
            content += url
            content += "\"><img class=\"preview\" src=\"../"
            content += url
            content += "\"></a>\n\t\t\t\t\t</div>\n"
        else:
            content += "\t\t\t\t\t<div class=\"message-file\">\n\t\t\t\t\t\t<div class=\"message-file-info\">\n\t\t\t\t\t\t\t<p class=\"message-file-name\">"
            content += name
            content += "</p><p class=\"message-file-type\">"
            content += mimetype
            content += "</p>\n\t\t\t\t\t\t</div>\n"
            if url:
                content += "\t\t\t\t\t\t<a href=\"../"
                content += url
                content += "\"><button class=\"download-button\"><i class=\"fa fa-download\"></i> Download</button></a>\n"
            content += "\t\t\t\t\t</div>\n"
    return content

def get_html_replies(replies, users, channel_names, emojis={}):
    # generates HTML for the replies under a message (thread)
    content = "\t\t\t\t\t<div class=\"message-thread-container\">\n"
    content += "\t\t\t\t\t\t<div class=\"message-thread\">\n"
    for m in replies:
        messageid = m.get("ts", "0").replace(".", "")
        timestamp = datetime.datetime.fromtimestamp(float(m.get("ts", "0"))).strftime("%Y-%m-%d %H:%M:%S")
        userid = m.get("user", "")
        username = users.get(userid, {}).get("name", "")
        avatar = users.get(userid, {}).get("avatar", "")
        msg_content = m.get("text", "")
        files = m.get("files", [])
        reactions = m.get("reactions", [])
        subtype = m.get("subtype", "")
        content += get_html_message(messageid, timestamp, username, avatar, msg_content, users, channel_names, files=files, reactions=reactions, subtype=subtype, emojis=emojis)
    content += "\t\t\t\t\t\t</div>\n"
    content += "\t\t\t\t\t</div>\n"
    return content

def get_html_reactions(reactions, emojis={}):
    # generates HTML for the reactions on a message
    content = "\t\t\t\t\t<div class=\"message-reactions\">\n"
    for r in reactions:
        name = r.get("name", "")
        count = r.get("count", 0)
        content += "\t\t\t\t\t\t<span class=\"reaction\">"
        content += parse_emoji_code(name, alt=":"+name+":", emojis=emojis)
        content += " <b>" + str(count) + "</b>"
        content += "</span>\n"
    content += "\t\t\t\t\t</div>\n"
    return content

def get_html_message(messageid, timestamp, username, avatar, msg_content, users, channel_names, channel_name="", replies=[], files=[], reactions=[], subtype="", search_result=False, emojis={}):
    # generates HTML for a message
    if search_result:
        stripped_message = strip_markup(msg_content, users, channel_names, emojis=emojis)
        if not stripped_message:
            return ""
    content = "\t\t\t\t<div class=\""
    content += "result" if search_result else "message"
    content += "-container\" id=\""
    content += messageid
    content += "\">\n\t\t\t\t\t<img src=\""
    content += "" if search_result else "../"
    content += avatar
    content += "\" class=\"user-icon\" />\n\t\t\t\t\t<div class=\"message\">\n"
    if not search_result:
        content += "\t\t\t\t\t\t<div class=\"username\">" + username + "</div>\n"
    content += "\t\t\t\t\t\t<a href=\""
    if search_result:
        content += "channels/" + channel_name + ".html"
    content += "#"
    content += messageid
    content += "\">\n\t\t\t\t\t\t\t<div class=\"time\">"
    content += timestamp
    content += "</div>\n\t\t\t\t\t\t</a>\n\t\t\t\t\t<div class=\"msg\">\n\t\t\t\t\t\t<p"
    if subtype and not search_result:
        content += " class=\"meta-msg\""
    content += ">"
    if search_result:
        content += stripped_message
        content += "</p>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class=\"msg-hidden\" hidden>\n\t\t\t\t\t\t<p>"
        content += stripped_message
    else:
        if subtype:
            content += parse_markup(escape_markup_chars(msg_content), users, channel_names, emojis=emojis)
        else:
            content += parse_markup(msg_content, users, channel_names, emojis=emojis)
    content += "</p>\n\t\t\t\t\t</div>\n"
    if not search_result:
        content += get_html_files(files)
        if replies:
            content += get_html_replies(replies, users, channel_names, emojis=emojis)
        if reactions:
            content += get_html_reactions(reactions, emojis=emojis)
    content += "\t\t\t\t</div>\n\t\t\t</div>\n"
    return content

def get_html_messages(messages, users, channel_names, search_result=False, emojis={}):
    # generates HTML for all messages
    content = ""
    for m in messages:
        messageid = m.get("ts", "0").replace(".", "")
        timestamp = datetime.datetime.fromtimestamp(float(m.get("ts", "0"))).strftime("%Y-%m-%d" if search_result else "%Y-%m-%d %H:%M:%S")
        userid = m.get("user", "")
        username = users.get(userid, {}).get("name", "")
        avatar = users.get(userid, {}).get("avatar", "")
        msg_content = m.get("text", "")
        channel_name = m.get("home_channel_name", "")
        replies = m.get("replies", [])
        files = m.get("files", [])
        reactions = m.get("reactions", [])
        subtype = m.get("subtype", "")
        content += get_html_message(messageid, timestamp, username, avatar, msg_content, users, channel_names, channel_name=channel_name, replies=replies, files=files, reactions=reactions, subtype=subtype, search_result=search_result, emojis=emojis)
    return content

def write_html(workspace_title, current_channel, msg_data, channels, dst, users, channel_names, emojis={}):
    # generates HTML for the content pages and writes it to file
    f = open(dst, "w", encoding="utf-8")
    header = get_html_head(workspace_title, current_channel)
    sidebar = get_html_sidebar(channels, current_channel)
    messages = get_html_messages(msg_data, users, channel_names, emojis=emojis)
    body = get_html_body(workspace_title, sidebar, messages)
    f.write(header)
    f.write(body)
    f.close()

def write_index_html(dst, channels, users, workspace_title, channel_names, subtitle="", complete_msg_data=[], emojis={}):
    # generates HTML for the index page and writes it to file
    f = open(dst, "w", encoding="utf-8")
    header = get_html_head(workspace_title, "Index", is_index=True)
    sidebar = get_html_sidebar(channels, is_index=True)
    content = "\t\t\t\t<div class=index_contents>\n\t\t\t\t\t<h1>"+workspace_title+"</h1>\n"
    if subtitle:
        content += "\t\t\t\t\t<h2>" + subtitle + "</h2>\n"
    content += "\t\t\t\t\t<div class=\"searchbar\">\n\t\t\t\t\t\t<input id=\"searchbar-textfield\" type=\"text\" placeholder=\"Search...\">\n\t\t\t\t\t</div>\n"
    content += "\t\t\t\t\t<div class=\"search-results\">\n"
    content += get_html_messages(complete_msg_data, users, channel_names, search_result=True, emojis=emojis)
    content += "\t\t\t\t\t</div>\t\t\t\t</div>\n"
    body = get_html_body(workspace_title, sidebar, content, is_index=True)
    f.write(header)
    f.write(body)
    f.close()

def read_chat_files(dir):
    # read all chat files and return list of JSON contents
    dir_contents = list(map(lambda x: join(dir, x), listdir(dir)))
    files = [x for x in dir_contents if isfile(x) and splitext(x)[1] == ".json"]
    data = []
    for f in files:
        jf = open(f, "r", encoding="utf8")
        d = json.load(jf)
        data += d
        jf.close()
    return data

def main():
    # let user open Slack export directory
    root_dir = easygui.diropenbox(title="Select Slack export directory", default=getcwd())
    if not all([root_dir]):
        exit()

    # warn user if there is a folder for a channel for which the name is possibly incorrect
    # for some reason Slack messes up the names of the folders in the Slack export if the channel names contain special characters
    # this breaks the program and I have no idea how to fix it without manually changing the names of the folders
    if not all(map(lambda x: bool(re.match("^[a-zA-Z0-9_-]*$", x)), filter(lambda y: isdir(join(root_dir, y)), listdir(root_dir)))):
        easygui.msgbox("WARNING: some channel names contain special characters that may not be supported. Verify that all your channels are available in the final HTML. If this is not the case, manually change the name of the folder of that channel so that it is the same as in the channels.json file.")

    # let user enter workspace title
    workspace_title = easygui.enterbox("Enter workspace title", "Enter workspace title", " ".join(basename(root_dir).split(" ")[:3])[:32])
    if not workspace_title:
        workspace_title = " "

    # makes sure the required directories are created/emptied if necessary
    dirs_to_check = list(map(lambda x: join(getcwd(), x), ["channels", "avatars", "images", "other_files"]))
    for d in dirs_to_check:
        if not isdir(d):
            mkdir(d)
        for f in listdir(d):
            if isfile(join(d, f)):
                remove(join(d, f))

    # generates list of files and directories to read
    root_dir_contents = list(map(lambda x: join(root_dir, x), listdir(root_dir)))
    root_dir_files = [x for x in root_dir_contents if isfile(x) and splitext(x)[1] == ".json"]
    root_dir_dirs = [x for x in root_dir_contents if isdir(x)]

    # initializes required data structures
    workspace_data = {}
    msg_timestamps = []
    complete_msg_data = []

    # lookup table for special Slack emojis to HTML encoding for normal ones
    emojis = {"exclamation": "2757", "white_check_mark": "2705", "arrow_right": "27a1-fe0f", "large_blue_circle": "1f535", "eyes": "1f440", "+1": "1f44d", "-1": "1f44e", "arrow_forward": "25b6-fe0f", "raised_hands": "1f64c"}

    # fills workspace_data with the contents of all JSON files in root_dir
    for f in root_dir_files:
        jf = open(f, "r", encoding="utf-8")
        d = json.load(jf)
        workspace_data.update({splitext(basename(f))[0]: d})
        jf.close()

    # creates dict of users, mapping user ID to username and avatar url
    users = {}
    for u in workspace_data.get("users", []):
        imgurl = u.get("profile", {}).get("image_72", "")
        if imgurl:
            newurl = "avatars/" + u.get("id", "")+splitext(imgurl)[1]
            urllib.request.urlretrieve(imgurl, newurl)
            imgurl = newurl
        username = u.get("profile", {}).get("display_name", "")
        if not username:
            username = u.get("profile", {}).get("real_name", "")
        users.update({u.get("id", ""): {"name": username, "avatar": imgurl}})

    # creates dict of channels, mapping channel ID to name
    channel_names = {}
    for c in workspace_data.get("channels", []):
        channel_names.update({c.get("id", ""): c.get("name", "")})

    # convert JSON to HTML for each channel and write it to file
    for dir in root_dir_dirs:
        # read JSON files
        data = read_chat_files(dir)

        # download all external media and replace references with the local versions
        for m in data:
            fl = m.get("files", [])
            if fl:
                for f in fl:
                    fileurl = f.get("url_private_download", "")
                    if fileurl:
                        fileid = f.get("id", "")
                        filename = f.get("name", "")
                        mimetype = f.get("mimetype", "")
                        if "image" in mimetype:
                            newurl = "images/" + fileid + "_" + filename
                            urllib.request.urlretrieve(fileurl, newurl)
                            fileurl = newurl
                        else:
                            newurl = "other_files/" + fileid + "_" + filename
                            urllib.request.urlretrieve(fileurl, newurl)
                            fileurl = newurl
                        f.update({"url_private_download": fileurl})
            m.update({"files": fl})
            m.update({"home_channel_name": basename(dir)})

            # save references of emojis to their unicode representation when available
            bl = m.get("blocks", [])
            if bl:
                for b in bl:
                    for _e in b.get("elements", []):
                        for __e in _e.get("elements", []):
                            if __e.get("type", "") == "emoji":
                                emojis.update({__e.get("name", ""): __e.get("unicode", "")})
        
        # links messages that belong to a thread
        complete_msg_data += data
        replies_ids = list(reduce(lambda a,b: a+b, map(lambda x: x.get("replies", []), data)))
        messages = [x for x in data if {"user": x.get("user", ""), "ts": x.get("ts", "")} not in replies_ids]
        for m in messages:
            thread = m.get("replies", {})
            for r in thread:
                m.get("replies")
                r.update([x for x in data if {"user": x.get("user", ""), "ts": x.get("ts", "")} == r][0])
            m.update({"replies": thread})

        # sort channel names alphabetically (like in Slack)
        channels = list(map(lambda x: x.get("name", ""), workspace_data.get("channels", [])))
        channels.sort()

        # generate and write individual channel HTML
        write_html(workspace_title, basename(dir), messages, channels, join(getcwd(), join("channels", basename(dir)+".html")), users, channel_names, emojis=emojis)

        # keep timestamps for each message for the search functionality on the index page
        msg_timestamps += list(map(lambda x: float(x.get("ts", "0")), data))

    # sort all messages chronologically
    complete_msg_data.sort(key=lambda x: float(x.get("ts", "0")))

    # write index HTML file
    write_index_html(join(getcwd(), "index.html"), channels, users, workspace_title, channel_names, subtitle="Slack message archive: " + datetime.datetime.fromtimestamp(min(msg_timestamps)).strftime("%d %b %Y") + " - " + datetime.datetime.fromtimestamp(max(msg_timestamps)).strftime("%d %b %Y"), complete_msg_data=complete_msg_data, emojis=emojis)

main()

