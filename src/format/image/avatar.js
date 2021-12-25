import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class avatar extends Format
{
	name           = "Avatar/0";
	website        = "http://fileformats.archiveteam.org/wiki/AVATAR";
	ext            = [".avt"];
	mimeType       = "text/x-avatar0";
	forbiddenMagic = TEXT_MAGIC_STRONG;
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}
