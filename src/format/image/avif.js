import {Format} from "../../Format.js";

export class avif extends Format
{
	name       = "AV1 Image File Format";
	website    = "http://fileformats.archiveteam.org/wiki/AVIF";
	ext        = [".avif", ".avifs"];
	mimeType   = "image/avif";
	magic      = ["AV1 Image File Format bitmap", "ISO Media, AVIF Image", "image/avif"];
	converters = ["avifdec", "wuimg", `abydosconvert[format:${this.mimeType}]`];
}
