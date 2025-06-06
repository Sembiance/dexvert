import {Format} from "../../Format.js";

export class dap extends Format
{
	name       = "SlideShow for VBXE";
	website    = "http://fileformats.archiveteam.org/wiki/SlideShow_for_VBXE";
	ext        = [".dap"];
	fileSize   = 77568;
	converters = ["recoil2png"];
}
