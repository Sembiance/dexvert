import {Format} from "../../Format.js";

export class hotHelpText extends Format
{
	name           = "HotHelp Text";
	website        = "http://fileformats.archiveteam.org/wiki/HotHelp";
	ext            = [".txt", ".hdr"];
	forbidExtMatch = true;
	magic          = ["HotHelp Text", "HotHelp Header"];
	unsupported    = true;
}
