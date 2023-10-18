import {Format} from "../../Format.js";

export class tg1 extends Format
{
	name       = "COKE";
	website    = "http://fileformats.archiveteam.org/wiki/COKE_(Atari_Falcon)";
	ext        = [".tg1"];
	magic      = ["COKE format bitmap"];
	converters = ["deark[module:coke]", "recoil2png"];
}
