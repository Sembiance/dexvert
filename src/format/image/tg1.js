import {Format} from "../../Format.js";

export class tg1 extends Format
{
	name       = "COKE TG1";
	website    = "http://fileformats.archiveteam.org/wiki/COKE_(Atari_Falcon)";
	ext        = [".tg1"];
	magic      = ["COKE format bitmap", "deark: coke", /^fmt\/1587( |$)/];
	converters = ["deark[module:coke]", "wuimg[matchType:magic]", "recoil2png"];
}
