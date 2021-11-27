import {Format} from "../../Format.js";

export class microIllustrator extends Format
{
	name        = "Micro Illustrator";
	ext         = [".mic"];
	unsupported = true;
	notes       = "NOT the same as image/mil Micro Illustrator. Sadly. due to no known magic and how recoil2png/view64 will convert ANYTHING, we disable this for now.";
	converters  = ["recoil2png", "view64"];
}
