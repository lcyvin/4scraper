# 4scraper
## A 4chan thread scraper designed to pull Webms from /wsg/ and /gif/ threads (or anywhere else there might be webms)

Currently, this project is in its absolute infancy. While it works on MY computer, it may not work on yours. At this time, the default output to MPV works but with no forward/backward movement between the URLs provided. Further MPV control handling will need to be added along with a lot of code clean-up. 

**Requirements:**

MPV

All other requirements should be met with the default python 3.5 libraries. 

**Flags:**

- -o - Output - [mpv|print|write\*]
- -b - Board - any 4chan board code (wsg, gif, etc.)
- -f - Flag - flag to pass to MPV

\* May not work properly

I have no clue if this works on Windows or OSX, I haven't tested it there. I'd like to assume that at the very least this python script will run in cygwin, MAYBE powershell? OSX support equally ambiguous.
