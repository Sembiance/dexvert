import {Format} from "../../Format.js";

export class nortonGuide extends Format
{
	name       = "Norton Guide";
	website    = "https://en.wikipedia.org/wiki/Norton_Guides";
	ext        = [".ng"];
	magic      = ["Norton Guide"];
	converters = ["ng2html[matchType:magic]"];
}
