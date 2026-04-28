import {Format} from "../../Format.js";

export class professionalDraw extends Format
{
	name        = "Professional Draw Image";
	website     = "http://www.classicamiga.com/content/view/5037/62/";
	ext         = [".clips"];
	magic       = ["Professional Draw clip", "Professional Draw document", "Professional Draw page"];
	unsupported = true;	// candidate for future vibe coding, 746 unique files on discmaster. But I'd want to seperate out detection of clip/document/page as each is likely a different file type?
	notes       = "No known converter.";
}
