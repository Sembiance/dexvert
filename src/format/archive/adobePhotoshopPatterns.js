import {Format} from "../../Format.js";

export class adobePhotoshopPatterns extends Format
{
	name           = "Adobe Photoshop Patterns";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = ["Adobe Photoshop Pattern"];
	converters     = ["nconvert[format:patps][extractAll]"];
}
