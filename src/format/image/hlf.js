import {Format} from "../../Format.js";

export class hlf extends Format
{
	name       = "Hires Interlace";
	website    = "http://fileformats.archiveteam.org/wiki/Hires_Interlace";
	ext        = [".hlf"];
	byteCheck  = [{offset : 0, match : [0x00, 0x20]}];
	converters = ["recoil2png"];
}
