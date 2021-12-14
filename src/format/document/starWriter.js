import {Format} from "../../Format.js";

export class starWriter extends Format
{
	name       = "StarWriter Document";
	ext        = [".tpl"];
	magic      = ["StarWriter for MS-DOS document"];
	notes      = "Soffice claims to support this format, but it wouldn't do anything with my .TPL files.";
	converters = ["strings"];
}
