import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class avatar extends Format
{
	name           = "Avatar/0";
	website        = "http://fileformats.archiveteam.org/wiki/AVATAR";
	ext            = [".avt"];
	mimeType       = "text/x-avatar0";
	forbiddenMagic = TEXT_MAGIC;
	converters     = [`abydosconvert[format:${this.mimeType}]`]
}
