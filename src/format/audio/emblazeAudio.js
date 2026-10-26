import {Format} from "../../Format.js";

export class emblazeAudio extends Format
{
	name             = "Emblaze Audio";
	ext              = [".ea"];
	forbidExtMatch   = true;
	confidenceAdjust = () => -10;	// Reduce by 10 so that emblazeVideo2 matches first
	magic            = ["Emblaze Video/Audio (generic)"];
	converters       = ["vibe2wav[singleFile][renameOut]"];
}
