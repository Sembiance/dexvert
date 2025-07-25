import {Format} from "../../Format.js";

export class webp extends Format
{
	name          = "WebP Image";
	website       = "http://fileformats.archiveteam.org/wiki/WebP";
	ext           = [".webp"];
	mimeType      = "image/webp";
	magic         = ["WebP bitmap", /^WebP$/, /^RIFF.* Web\/P image/, "RIFF Datei: unbekannter Typ 'WEBP'", "Generic RIFF file WEBP", "Format: WebP", "image/webp", "piped webp sequence (webp_pipe)", "deark: riff (WebP)", /^fmt\/(566|567|568)( |$)/];
	untouched     = true;
	metaProvider = ["image", "webpinfo"];
}
