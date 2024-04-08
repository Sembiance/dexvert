import {Format} from "../../Format.js";

export class directMusicSegment extends Format
{
	name       = "DirectMusic Segment";
	ext        = [".dmsg"];
	magic      = ["Microsoft DirectMusic Segment", /^fmt\/957( |$)/];
	converters = ["vgmstream"];
}
