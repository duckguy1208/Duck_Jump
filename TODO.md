# TODO

## Defects

- [x] [HIGH_PRIORITY] We are in C:\Users\jonat\~projects\tie-and-jon-pygame yet there is a tie-and-jon-pygame directory in C:\Users\jonat\~projects\tie-and-jon-pygame. Investigate the cause of the duplication... could it be the wording in the gemini-task.ps1 script or prompt.md? Is it safe to remove the duplicate nested directory?
- [x] Platforms always need to be within reach of the duck's max jump height. No impossible platforms.
- [x] Sounds need converting from mp3 to ogg for git pages
- [x] Mobile tap controls dont function
- [x] Mobile screen is landscape rather than portai

## Features (priority sorted)

- [x] procedural generate platforms upward.
- [x] increment score as duck goes upward.
- [x] game over screen when falling off the bottom.
- [x] [HIGH PRIORITY] Use assets within assets/images for game
  - duck should use duck.png and duck_quack.png when quacking.
    1st level AKA screen height should use game_background.png, then progress as follows
    sky1 - sky5
    space1 - space4
    then progress through each colored background in any order.
    If the player gets through all the levels, they win. Implement a win screen like the game over screen.
- [x] start menu
- [x] pause menu
- [x] mobile support
- [x] optimize for portrait view on mobile, keep landscape on desktop (detect based on screen width, probably)
- [ ] more than one path up
- [ ] collapsing platforms
- [ ] custom platforms (not just white)
- [ ] reason to quack (could just be for fun too)
- [x] no ending (repeat space background)
- [ ] multiplayer functionality (racing)

## Tech Debt

- [x] implement proper linting that enforces python standards. Include the linting as part of a pre commit hook
- [x] implement automatic code formatting with prettier (or other if there is something more python focused). Add .vscode/settings.json to ensure all devs automtically have formatting on save/paste.

## Deployment

- [x] FInish implementing Pygbag to prepare the game to be deployed as a PWA on github pages.
