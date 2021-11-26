import {Format} from "../../Format.js";

export class deskMatePaint extends Format
{
	name       = "DeskMate Paint";
	website    = "http://fileformats.archiveteam.org/wiki/DeskMate_Paint";
	ext        = [".pnt"];
	magic      = ["DeskMate Paint image"];
	converters = ["deark", "recoil2png"]
}
