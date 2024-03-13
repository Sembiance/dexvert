import {Format} from "../../Format.js";

export class rockyInterlace extends Format
{
	name       = "Rocky Interlace Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Rocky_Interlace_Picture";
	ext        = [".rip"];
	magic      = ["Rocky Interlace Picture bitmap", /^fmt\/1746( |$)/];
	converters = ["recoil2png"];
}
