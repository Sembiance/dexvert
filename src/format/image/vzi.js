import {Format} from "../../Format.js";

export class vzi extends Format
{
	name          = "VertiZontal Interlacing";
	website       = "http://fileformats.archiveteam.org/wiki/VertiZontal_Interlacing";
	ext           = [".vzi"];
	fileSize      = 16000;
	matchFileSize = true;
	converters    = ["recoil2png"];
}
