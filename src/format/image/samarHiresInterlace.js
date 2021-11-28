import {Format} from "../../Format.js";

export class samarHiresInterlace extends Format
{
	name       = "SAMAR Hires Interlace";
	website    = "http://fileformats.archiveteam.org/wiki/SAMAR_Hires_Interlace";
	ext        = [".shc"];
	fileSize   = 17920;
	converters = ["recoil2png"];
}
