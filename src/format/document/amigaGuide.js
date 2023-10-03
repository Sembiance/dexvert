import {Format} from "../../Format.js";

export class amigaGuide extends Format
{
	name       = "Amigaguide Document";
	website    = "http://fileformats.archiveteam.org/wiki/AmigaGuide";
	ext        = [".guide"];
	magic      = ["Amigaguide hypertext document", "AmigaGuide file"];
	converters = ["grotag", "guideml", "strings"];
}
