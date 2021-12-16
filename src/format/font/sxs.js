import {Format} from "../../Format.js";

export class sxs extends Format
{
	name       = "Atari SXS Font";
	ext        = [".sxs"];
	fileSize   = 1030;
	converters = ["recoil2png"];
}
