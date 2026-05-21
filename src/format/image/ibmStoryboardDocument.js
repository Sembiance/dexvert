import {Format} from "../../Format.js";

export class ibmStoryboardDocument extends Format
{
	name           = "IBM Storyboard Text Maker Document";
	website        = "http://fileformats.archiveteam.org/wiki/IBM_Storyboard_Text_Maker_Document";
	ext            = [".txm"];
	forbidExtMatch = true;
	magic          = ["IBM Storyboard screen Capture", "deark: storyboard (Storyboard picture (old))"];
	weakMagic      = true;
	converters     = ["vibeExtract[singleFile][renameOut] -> ansilove[format:ans]"];
}
