# Slack archive visualizer
This is a tool that converts JSON [Slack archives](https://slack.com/help/articles/201658943-Export-your-workspace-data) to HTML pages that can be viewed locally with a browser.

![2022-12-12 00_27_18-Greenshot - Copy](https://user-images.githubusercontent.com/78315156/206935341-11319f35-edb0-4f53-b539-55f06f8cb952.png)

### Requirements
-   have  **Python**  installed (I tested it on Python 3.10)
-   have the  **easygui**  module installed (can be done by running  `pip install easygui`  after installing Python)

### How to run
Run the slack-archive-visualizer.py file. Make sure the working directory is set to that of the .py file, so make sure to `cd` to the correct directory when using command line. Afterwards, all required files can then be found in that directory.

### Features
-   The index page contains a search bar with which all messages in all channels can be searched. Clicking on the timestamp of a message will open up the full message.
    ![2022-12-12 00_12_15-Index - Test Workspace Slack](https://user-images.githubusercontent.com/78315156/206935529-26da0e39-237e-4343-ad2b-527c61f9c7b7.png)
-   have the  **easygui**  module installed (can be done by running  `pip install easygui`  after installing Python)

### Problems
I initially wrote this purely for personal use. Because of this, the code is quite messy. Also, I only implemented the features I needed myself. This means that there are some problems I didn't bother fixing.
 - The code is still quite messy
 - For some reason, Slack mojibakes the names of the folders in the archive of they contain any special or non-latin characters. This is really bad with for instance Japanese names, which will cause the folder names to basically be random text. This is a problem because these folder names are also key in linking the chat JSON files to the channel info in channels.json. I have not found a way to fix this automatically, so at the moment all folders in the Slack archive with mojibaked names need to be corrected manually for the visualizer to work.
 - Slack uses some proprietary format in which to store emojis. I created a small lookup table for emojis I use myself. Any emojis not in this lookup table will not load properly in the final HTML page. The program will print a warning to notify the user if an emoji was used that could not be found in the lookup table.
 - I used the free version of Slack, so any features that can only be used with the paid version are most definitely NOT implemented (DMs for instance).

### Future plans
Since I don't use Slack anymore, I don't plan on working on it any further in the foreseeable future.
