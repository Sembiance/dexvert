import {Format} from "../../Format.js";

export class amigaGuide extends Format
{
	name    = "Amigaguide Document";
	website = "http://fileformats.archiveteam.org/wiki/AmigaGuide";
	ext     = [".guide"];
	magic   = ["Amigaguide hypertext document", "AmigaGuide file"];
	
	// Used to use 'guideml' but it's just waaaay too buggy and hangs on almost every guide, often locking up files on the amiga.
	// So we just do grotag and strings now
	converters    = ["grotag", "strings"];
}
