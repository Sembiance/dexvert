import {Format} from "../../Format.js";

export class paintShop extends Format
{
	name       = "PaintShop";
	website    = "http://fileformats.archiveteam.org/wiki/PaintShop";
	ext        = [".da4", ".psc"];
	magic      = ["PaintShop plus Compressed bitmap"];
	converters = ["recoil2png"];
}
