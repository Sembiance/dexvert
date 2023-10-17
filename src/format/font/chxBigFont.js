import {Format} from "../../Format.js";

export class chxBigFont extends Format
{
	name       = "CHX Big Font";
	ext        = [".chx"];
	magic      = ["CHX font format"];
	converters = ["recoil2png"];
}
