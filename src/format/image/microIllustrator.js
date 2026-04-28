import {Format} from "../../Format.js";

export class microIllustrator extends Format
{
	name        = "Micro Illustrator";
	ext         = [".mic", ".mil"];
	mimeType    = "image/x-micro-illustrator";
	unsupported = true;	// no known magic and extensions not reliable and since recoil2png/view64 will convert ANYTHING, we disable this for now (NOTE: This is NOT the same as image/mil)
	converters  = ["recoil2png[format:MIC]", "view64"];	// abydos has support for the 'uncompressed' version, ".mil" support
}
