import {Format} from "../../Format.js";

export class professionalDraw extends Format
{
	name        = "Professional Draw Image";
	website     = "http://www.classicamiga.com/content/view/5037/62/";
	ext         = [".clips"];
	magic       = ["Professional Draw clip", "Professional Draw document", "Professional Draw page"];
	unsupported = true;
	notes       = "No known converter.";
}
