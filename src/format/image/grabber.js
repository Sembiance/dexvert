import {xu} from "xu";
import {Format} from "../../Format.js";

export class grabber extends Format
{
	name           = "Grabber";
	website        = "http://fileformats.archiveteam.org/wiki/GRABBER";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	magic          = ["GRABBER COM", /16bit DOS (EXE|COM) GRABBER/];
	converters     = [`dosEXEScreenshot[timeout:${xu.SECOND*15}][frameLoc:95]`];
}
