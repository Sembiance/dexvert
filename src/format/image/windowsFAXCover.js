import {Format} from "../../Format.js";

export class windowsFAXCover extends Format
{
	name        = "Windows FAX Cover";
	ext         = [".cpe"];
	magic       = ["Windows FAX cover"];
	unsupported = true;
}
