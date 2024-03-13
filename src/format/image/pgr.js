import {Format} from "../../Format.js";

export class pgr extends Format
{
	name       = "PowerGraphics";
	website    = "http://fileformats.archiveteam.org/wiki/PowerGraphics";
	ext        = [".pgr"];
	magic      = ["PowerGraphics bitmap", /^fmt\/1731( |$)/];
	converters = ["recoil2png"];
}
