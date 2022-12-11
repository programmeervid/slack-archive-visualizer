# Slack archive visualizer
HTML visualizer for JSON Slack archives

### Requirements
-   have  **Python**  installed (I tested it on Python 3.10)
-   have the  **easygui**  module installed (can be done by running  `pip install easygui`  after installing Python)

### How to use
Run the slack-archive-visualizer.py file. Make sure the working directory is set to that of the .py file, so make sure to `cd` to the correct directory when using command line. Afterwards, all required files can then be found in that directory.

### Problems
I initially wrote this purely for personal use. Because of this, the code is quite messy. Also, I only implemented the features I needed myself. This means that there are some problems I didn't bother fixing.
 - The code is still quite messy
 - For some reason, Slack mojibakes the names of the folders in the archive of they contain any special or non-latin characters. This is really bad with for instance Japanese names, which will cause the folder names to basically be random text. This is a problem because these folder names are also key in linking the chat JSON files to the channel info in channels.json. I have not found a way to fix this automatically, so at the moment all folders in the Slack archive with mojibaked names need to be corrected manually for the visualizer to work.
 - Slack uses some proprietary format in which to store emojis. I created a small lookup table for emojis I use myself. Any emojis not in this lookup table will not load properly in the final HTML page. The program will print a warning to notify the user if an emoji was used that could not be found in the lookup table.
 - I used the free version of Slack, so any features that can only be used with the paid version are most definitely NOT implemented (DMs for instance).

### Future plans
Since I don't use Slack anymore, I don't plan on working on it any further in the foreseeable future.
