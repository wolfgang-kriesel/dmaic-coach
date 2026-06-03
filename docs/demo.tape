# Render with:  vhs docs/demo.tape   (run from the repo root, after `make setup`)
# Produces docs/demo.gif
Output docs/demo.gif

Set Shell bash
Set FontSize 14
Set Width 1280
Set Height 900
Set Theme "Dracula"
Set Padding 18
Set Framerate 20
Set TypingSpeed 45ms

Hide
Type "source .venv/bin/activate && clear"
Enter
Sleep 1s
Show

Type "make demo"
Sleep 700ms
Enter
Sleep 13s
