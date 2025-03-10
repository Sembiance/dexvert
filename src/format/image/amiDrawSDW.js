import {Format} from "../../Format.js";

export class amiDrawSDW extends Format
{
	name       = "AmiDraw SDW";
	website    = "http://fileformats.archiveteam.org/wiki/SDW_(AmiDraw)";
	ext        = [".sdw"];
	magic      = ["AmiDraw Drawing", /^x-fmt\/290( |$)/];
	weakMagic  = true;
	converters = ["keyViewPro"];
}
