# TODO

## Defects

- [x] [HIGH_PRIORITY] We are in C:\Users\jonat\~projects\tie-and-jon-pygame yet there is a tie-and-jon-pygame directory in C:\Users\jonat\~projects\tie-and-jon-pygame. Investigate the cause of the duplication... could it be the wording in the auto-work.ps1 script or prompt.md? Is it safe to remove the duplicate nested directory?
- [x] Platforms always need to be within reach of the duck's max jump height. No impossible platforms.
- [x] Sounds need converting from mp3 to ogg for git pages
- [x] Mobile tap controls dont function
- [x] Mobile screen is landscape rather than portait

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
- [ ] Ensure there is sometimes more than one path up that the duck can take using the platforms. Ensure platforms do not overlap. Essentially, we need more platforms so that there are times when the player has multilple options on how to proceed. This will set us up for other features like having broken or instantly collapsing platforms, enemies on platforms, other obstacles that would make one path preferable over another.
- [ ] collapsing platforms that are visually distinct from other platforms and break apart after the player stands on them for more than 2 seconds. When the platform breaks, it no longer supports the player and the player falls. When the platform breaks, the player can no longer jump from the platform. The platform should indicate that it is breaking at 1 second and then break at the next second (breaks in 2 seconds).
- [ ] custom platforms (not just white)
- [ ] reason to quack (could just be for fun too)
- [x] no ending (repeat space background)
- [ ] Create a MuliplayerIdeas.md in the docs folder to weight pros and cons of multiple options for implementing multiplayer functionality (racing) for this game. Should include considerations such as hosting options, backend support in python (ideally)... maybe hosting the backend separately so that the front end can remain on github pages.

## Tech Debt

- [x] implement proper linting that enforces python standards. Include the linting as part of a pre commit hook
- [x] implement automatic code formatting with prettier (or other if there is something more python focused). Add .vscode/settings.json to ensure all devs automtically have formatting on save/paste.
- [] Move game code into a 'src' folder except for 'main' which should remain in the project root so that the game can be run in the project root with `python main.py`... should follow best practices for python/pygame project organization.
- [] Break out classes that are defined within files that have other classes. Follow one class per file/module.
- [] Identify util methods defined throughout the project and move them to a utils.py module to improve code organization and reduce code duplication throughout the codebase.

## Deployment

- [x] Finish implementing Pygbag to prepare the game to be deployed as a PWA on github pages.
- [] In meta quest, the website (github page) can be 'Added to library' or 'Added to homescreen'. Let's ensure we have the assets and project configuration necessary to ensure a positive and complete consumer experience. If you need human involvement in this, write what needs to be done within a markdown file inside the docs folder in the project root.
