import {Format} from "../../Format.js";

export class directMusicSegment extends Format
{
	name       = "DirectMusic Segment";
	ext        = [".dmsg"];
	magic      = ["Microsoft DirectMusic Segment", "RIFF Datei: unbekannter Typ 'DMSG'", "Generic RIFF file DMSG", /^fmt\/957( |$)/];
	converters = ["vgmstream"];
}
