import {Format} from "../../Format.js";

export class cin extends Format
{
	name       = "Kodak Cineon";
	website    = "http://fileformats.archiveteam.org/wiki/Cineon";
	ext        = [".cin"];
	mimeType   = "image/x-cineon";
	magic      = ["Kodak Cineon bitmap", "Cineon image data", "Kodak Cineon :cin:"];
	converters = ["nconvert[format:cin]", "iconvert", `abydosconvert[format:${this.mimeType}]`];
}
