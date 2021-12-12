import {Format} from "../../Format.js";

export class amigaGuide extends Format
{
	name         = "Amigaguide Document";
	website      = "http://fileformats.archiveteam.org/wiki/AmigaGuide";
	ext          = [".guide"];
	magic        = ["Amigaguide hypertext document", "AmigaGuide file"];
	keepFilename = true;
	auxFiles     = (input, otherFiles, otherDirs) => ((otherFiles.length>0 || otherDirs.length>0) ? [...otherFiles, ...otherDirs] : false);	// Amiga Guides reference other guides and directories, so include symlinks to everything else
	
	// Grotag is best because it'll have access to the 'otherFiles' and 'otherDirs'
	// If that fails though, guideml will at least process the text content in this particular guide file
	// Finally we fall back to strings
	converters    = ["grotag", "guideml", "strings"];
}
