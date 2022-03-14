import {Format} from "../../Format.js";

export class xvThumbnail extends Format
{
	name       = "XV Thumbnail";
	magic      = ["XV thumbnail image data"];
	converters = ["nconvert"];
}
