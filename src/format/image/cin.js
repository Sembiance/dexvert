import {Format} from "../../Format.js";

export class cin extends Format
{
	name       = "Kodak Cineon";
	website    = "http://fileformats.archiveteam.org/wiki/Cineon";
	ext        = [".cin"];
	mimeType   = "image/x-cineon";
	magic      = ["Kodak Cineon bitmap", "Cineon image data"];
	converters = ["nconvert", "iconvert", `abydosconvert[format:${this.mimeType}]`];
}
