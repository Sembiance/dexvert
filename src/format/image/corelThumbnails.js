import {xu} from "xu";
import {Format} from "../../Format.js";

export class corelThumbnails extends Format
{
	name       = "Corel Thumbnails Archive";
	website    = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	filename   = [/^_thumbnail_/i];
	converters = ["vibeExtract[skipVerify]"];
}
