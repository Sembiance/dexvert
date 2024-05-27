import {Format} from "../../Format.js";

export class nortonGuide extends Format
{
	name       = "Norton Guide/Expert Help";
	website    = "https://en.wikipedia.org/wiki/Norton_Guides";
	ext        = [".ng"];
	magic      = ["Norton Guide", "Expert Help hypertext"];
	converters = ["ng2html[matchType:magic]"];
}
