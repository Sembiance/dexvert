import {Format} from "../../Format.js";

export class webp extends Format
{
	name          = "WebP Image";
	website       = "http://fileformats.archiveteam.org/wiki/Webp";
	ext           = [".webp"];
	mimeType      = "image/webp";
	magic         = ["WebP bitmap", /^WebP$/, /^RIFF.* Web\/P image$/];
	untouched     = true;
	metaProvider = ["image", "webpinfo"];
}
