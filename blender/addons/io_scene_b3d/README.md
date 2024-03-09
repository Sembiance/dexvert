# io_scene_b3d

Blender Import-Export script for Blitz 3D .b3d files

## Disclaimer

I don't have much time to maintain this and I get no PR's, so there are more recent forks:

* https://github.com/GreenXenith/io_scene_b3d (recommended by [minetest wiki](https://wiki.minetest.net/Using_Blender#Exporting_B3D))
* https://github.com/joric/io_scene_b3d/network (other forks)

## Download

You may download plugin zip in the [releases](https://github.com/joric/io_scene_b3d/releases) section

## Installation

* Userspace method: click "File" - "User Preferences" - "Add-ons" - "Install Add-on from File".
The add-on zip file should contain io_scene_b3d directory, including the directory itself.
* Alternative method: copy or symlink the io_scene_b3d directory to blender user directory, e.g. to
`%APPDATA%\Blender Foundation\Blender\2.80\scripts\addons\io_scene_b3d`. Then search for b3d and enable add-on in "Preferences" - "Add-ons". Click "Save User Settings" afterwards.

## Debugging

* Userspace method: every time you make a change the script has to be reloaded (press F3, search for Reload Scripts).
* Alternative method: my shortcut, Shift+Ctrl+F in Object Mode. It resets scene, reloads the script and imports test file.

## TODO

### Import

* Animation is not yet implemented in version 1.0. Check master branch for updates.
* Nodes use original quaternion rotation that affects user interface.
Maybe convert them into euler angles.

## License

This software is covered by GPL 2.0. Pull requests are welcome.

* The import script based on a heavily rewriten (new reader) script from Glogow Poland Mariusz Szkaradek.
* The export script uses portions of script by Diego 'GaNDaLDF' Parisi (ported to Blender 2.8) under GPL license.
* The b3d format documentation (b3dfile_specs.txt) doesn't have a clear license (I assume Public Domain).

## Alternatives

* [Assimp](http://assimp.sourceforge.net/) - doesn't read .b3d animation in most cases, maybe I have acquired a very particular set of files
* [fragMOTION](http://www.fragmosoft.com/) - works fine most of the time, but it's a terrible nagware and the only suitable export is .smd

## References

* https://github.com/joric/gnome

