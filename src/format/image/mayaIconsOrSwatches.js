import {Format} from "../../Format.js";

export class mayaIconsOrSwatches extends Format
{
	name           = "Maya Icons/Swatches";
	ext            = [".swatches"];
	forbidExtMatch = true;
	magic          = [/^fmt\/1168( |$)/];
	converters     = ["wuimg[format:mayaicon]"];
}
