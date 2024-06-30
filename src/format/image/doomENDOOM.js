import {Format} from "../../Format.js";

export class doomENDOOM extends Format
{
	name         = "Doom ENDOOM Screen";
	website      = "https://doomwiki.org/wiki/ENDOOM";
	filename     = [/endoom/i];		// sometimes it's an extension, or just the name, or somewhere in the name
	weakFilename = true;
	fileSize     = 4000;
	converters   = ["endoom2ans"];
}
