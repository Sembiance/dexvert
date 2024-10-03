import {Format} from "../../Format.js";

export class granny3DModel extends Format
{
	name        = "Granny 3D Model";
	website     = "http://fileformats.archiveteam.org/wiki/COLLADA";
	ext         = [".gr2"];
	magic       = ["Granny 3D model"];
	unsupported = true;
	notes       = "I tried using https://github.com/SWTOR-Slicers/Granny2-Plug-In-Blender-2.8x but it didn't work for any of the old GR2 models I gave it. Found another imported but it says it only works for Metin2 game models";
}
