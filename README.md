# CircleFightsBack

A 2D physics-based game built in Python using Pygame. If you wanna see the current gameplay check out the first commit called `v 0.1.0`. Code overhaul is currently happening what to expect is shown below.
To check out the current version run the file Main.py although you'll need to adjust some code to see all its functions.

## In the V 0.2.0 Code Overhaul
- Utilises ECS Paradigm to improve performance dramatically to allow 1000 entities in screen
- Cleaner Codebase by seperating Big main file into smaller more manageable files. You should see this already
- Collision is improved where polygons, circles and rectangle can all collide each other. This is also includes dyanmic objects interaction where objects not overlap by resolving themselves with physics
- Physics is the same except as said before improved collision resolvement so enemies don't overlap anymore
- Improved rendering by allowing multiple different layers to be put on screen in different parts of the foreground. UI will always be shown at the front with tranperent objects not being ahead of them
- enemies can now be planned to have dual elements due to ECS system
- Rooted out Numpy with a lightweight vector calculator file known as Vector.py to increase performance
