import {Format} from "../../Format.js";

export class hs2 extends Format
{
	name       = "HS2 Postering";
	website    = "http://fileformats.archiveteam.org/wiki/HS2_(POSTERING)";
	ext        = [".hs2"];
	converters = ["deark[module:hs2]", "recoil2png"];
}
