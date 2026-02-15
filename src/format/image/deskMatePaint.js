import {Format} from "../../Format.js";

export class deskMatePaint extends Format
{
	name           = "DeskMate Paint";
	website        = "http://fileformats.archiveteam.org/wiki/DeskMate_Paint";
	ext            = [".pnt"];
	forbidExtMatch = true;
	magic          = ["DeskMate Paint image", "DeskMate Paint Alt", "deark: deskmate_pnt"];
	converters     = ["deark[module:deskmate_pnt]", "recoil2png[format:PNT.TandyPnt,PNT.Paintworks]"];
}
