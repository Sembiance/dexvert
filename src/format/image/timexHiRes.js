import {Format} from "../../Format.js";

export class timexHiRes extends Format
{
	name       = "Timex 2048 Hi-Res";
	ext        = [".scr"];
	fileSize   = 12289;
	converters = ["recoil2png"];
}
