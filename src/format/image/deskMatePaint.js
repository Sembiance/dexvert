import {Format} from "../../Format.js";

export class deskMatePaint extends Format
{
	name           = "DeskMate Paint";
	website        = "http://fileformats.archiveteam.org/wiki/DeskMate_Paint";
	ext            = [".pnt"];
	forbidExtMatch = true;
	magic          = ["DeskMate Paint image", "DeskMate Paint Alt"];
	converters     = ["deark", "recoil2png"];
}
