import {Format} from "../../Format.js";

export class amigaVisionFlow extends Format
{
	name        = "Amiga Vision Flow";
	website     = "https://archive.org/details/AmigaVision_1990_Commodore_363394-01/page/n15/mode/2up";
	ext         = [".avf"];
	magic       = ["Amiga Vision Flow"];
	unsupported = true;	// the 186 unique files on discmaster mostly just animate/playback/direct already existing and converted external files
}
