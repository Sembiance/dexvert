import {Format} from "../../Format.js";

export class macBinaryImage extends Format
{
	name           = "MacBinary Image";
	magic          = ["Macintosh JPEG bitmap (MacBinary)", "Macintosh TIFF bitmap (MacBinary)", "Mac PNG bitmap (MacBinary)", "Mac BMP bitmap (MacBinary)", "Mac JPEG 2000 bitmap (MacBinary)"];
	converters     = ["deark[mac][alwaysConvert]"];
	notes          = "Some images from old Mac systems have resource forks and are encoded in MacBinary. The resource forks are usually just an icon, so too useful to save.";
}
