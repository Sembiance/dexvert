import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class iCEDraw extends Format
{
	name           = "iCEDraw Format";
	website        = "http://fileformats.archiveteam.org/wiki/ICEDraw";
	ext            = [".idf"];
	mimeType       = "image/x-icedraw";
	magic          = ["iCEDraw graphic"];
	forbiddenMagic = TEXT_MAGIC;
	metaProvider   = ["ansiArt"];
	converters     = ["ansilove[format:idf]", `abydosconvert[format:${this.mimeType}]`];
}
