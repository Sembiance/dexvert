import {Format} from "../../Format.js";

export class armAPAAImage extends Format
{
	name           = "ArmA PAA Image";
	ext            = [".paa"];
	forbidExtMatch = true;
	magic          = [/^geViewer: PBO_SREV_PAA( |$)/];
	converters     = ["gameextractor[renameOut][codes:PBO_SREV_PAA]"];
}
