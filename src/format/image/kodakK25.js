import {Format} from "../../Format.js";

export class kodakK25 extends Format
{
	name       = "Kodak DC25";
	website    = "http://fileformats.archiveteam.org/wiki/Kodak";
	ext        = [".k25"];
	fileSize   = [77888, 140_352];
	magic      = [/^TIFF image data.*model=KODAK DC25/];
	mimeType   = "image/x-kodak-k25";
	converters = [`abydosconvert[format:${this.mimeType}]`]
}
