import {Format} from "../../Format.js";

export class windowsFAXCover extends Format
{
	name           = "Windows FAX Cover";
	ext            = [".cpe"];
	forbidExtMatch = true;
	magic          = ["Windows FAX cover"];
	converters     = ["vibe2png"];
}
