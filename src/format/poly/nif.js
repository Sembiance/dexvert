import {Format} from "../../Format.js";

export class nif extends Format
{
	name       = "NetImmerse NIF";
	website    = "http://fileformats.archiveteam.org/wiki/NIF";
	ext        = [".nif"];
	magic      = ["NetImmerse file format", "NetImmerse Format", "GameBryo file format", "Gamebryo game engine file"];
	converters = ["blender[format:nif]"];
	notes	   = "Blender doesn't handle all formats. Could use 'Nifskope' to try to convert more, but it won't run under win2k, winxp, win7 or wine/wine64. It does run on Linux, but no command line conversion that I could tell.";
}
