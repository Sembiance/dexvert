import {Format} from "../../Format.js";

export class ftc extends Format
{
	name       = "Falcon True Color";
	website    = "http://fileformats.archiveteam.org/wiki/Falcon_True_Color";
	ext        = [".ftc"];
	fileSize   = 184_320;
	converters = ["recoil2png"];
}
