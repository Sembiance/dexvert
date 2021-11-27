import {Format} from "../../Format.js";

export class magicPainter extends Format
{
	name       = "Magic Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Magic_Painter";
	ext        = [".mgp"];
	magic      = ["Magic Painter bitmap"];
	fileSize   = 3845;
	converters = ["recoil2png"]
}
