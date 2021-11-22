import {Format} from "../../Format.js";

export class jpg extends Format
{
	name          = "Joint Photographic Experts Group Image";
	website       = "http://fileformats.archiveteam.org/wiki/JPG";
	ext           = [".jpg", ".jpeg", ".jpe", ".jfif"];
	mimeType      = "image/jpeg";
	magic         = ["JFIF JPEG bitmap", "JPEG image data", "JPEG bitmap", "JPEG File Interchange Format"];
	fallback      = true;	// Some other formats such as image/a4r can be mistaken for JPEG data by 'file' command, so we ensure we try other formats first before falling back to this
	untouched     = true;
	metaProviders = ["image"];
}
