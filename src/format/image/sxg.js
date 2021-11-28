import {Format} from "../../Format.js";

export class sxg extends Format
{
	name       = "Speccy eXtended Graphic";
	ext        = [".sxg"];
	magic      = ["Speccy eXtended Graphics bitmap"];
	converters = ["recoil2png"];
}
