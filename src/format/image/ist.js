import {Format} from "../../Format.js";

export class ist extends Format
{
	name       = "Atari Interlace Studio";
	website    = "http://madteam.atari8.info/index.php?prod=uzytki";
	ext        = [".ist"];
	fileSize   = 17184;
	converters = ["recoil2png"]
}
