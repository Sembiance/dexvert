import {xu} from "xu";
import {Format} from "../../Format.js";

export class redStormRSB extends Format
{
	name           = "Red Storm RSB";
	ext            = [".rsb"];
	forbidExtMatch = true;
	magic          = ["Red Storm File Format :rsb:", /^geViewer: RSB( |$)/];
	converters     = ["nconvert[format:rsb]", "gameextractor[renameOut][codes:RSB]"];
}
