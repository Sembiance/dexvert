import {Format} from "../../Format.js";

export class q4 extends Format
{
	name       = "XLD4 Image";
	website    = "http://fileformats.archiveteam.org/wiki/XLD4";
	ext        = [".q4"];
	magic      = ["XLD4 bitmap", /^fmt\/1447( |$)/];
	converters = ["recoil2png"];
}
