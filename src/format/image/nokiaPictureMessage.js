import {Format} from "../../Format.js";

export class nokiaPictureMessage extends Format
{
	name       = "Nokia Picture Message";
	website    = "http://fileformats.archiveteam.org/wiki/Nokia_Picture_Message";
	ext        = [".npm"];
	magic      = ["Nokia Picture Message bitmap", /^fmt\/1896( |$)/];
	converters = ["deark[module:npm][strongMatch]", "nconvert"];
}
