import {Format} from "../../Format.js";

export class cmp extends Format
{
	name       = "LEADTools Compressed Image";
	website    = "http://fileformats.archiveteam.org/wiki/CMP";
	ext        = [".cmp"];
	magic      = ["LEADTools CMP Image Compressed bitmap", "LEADToolsCompressed Image", /^fmt\/1337( |$)/];
	converters = ["leadecom"];
}
