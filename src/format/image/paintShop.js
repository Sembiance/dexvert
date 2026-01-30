import {Format} from "../../Format.js";

export class paintShop extends Format
{
	name       = "PaintShop";
	website    = "http://fileformats.archiveteam.org/wiki/PaintShop_(Atari_ST)";
	ext        = [".da4", ".psc"];
	magic      = ["PaintShop plus Compressed bitmap", /^fmt\/1733( |$)/];
	converters = ["wuimg[format:da4][matchType:magic]", "recoil2png"];
}
