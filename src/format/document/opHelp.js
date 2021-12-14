import {Format} from "../../Format.js";

export class opHelp extends Format
{
	name        = "OPHelp";
	ext         = [".hlp"];
	magic       = ["OPHelp Help"];
	unsupported = true;
	notes       = "Couldn't locate additional info for it";
}
