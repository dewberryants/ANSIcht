# ansi.e

<img alt="Screenshot" src="docs/screen.webp"/>

# Description
ansi.e is a simple text art editor that supports
24bit colors and unicode text. Right now, the feature
set is very limited to single-pixel drawing.

A color palette remembers the 12 recently used colors.

This was developed for a personal game project, and
I'm happy to share it with everybody!

Currently, ansi.e exports and reads from .txt files
containing characters and ANSI escape sequences.

# Installation
    git clone https://github.com/dewberryants/ansidote.git
    cd ansidote
    pip install . --user

# Use
    ansidote

Right-click on the image picks the color/symbol combination of
the clicked pixel. To change color, left-click on the FG/BG colors
on the tool bar to the right or use on of the colors from, history,
where left click picks it as FG and right-click picks it as BG color.
The bordered preview shows the currently active brush.

# Known Issues
 * No scrolling on palette / character map
 * Dark Mode Only

# Closing Words

Many thanks go out to the developers of pygame,
which ansi.e is mostly developed in.

Happy painting!
