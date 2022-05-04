import {Format} from "../../Format.js";

export class jpg extends Format
{
	name             = "Joint Photographic Experts Group Image";
	website          = "http://fileformats.archiveteam.org/wiki/JPG";
	ext              = [".jpg", ".jpeg", ".jpe", ".jfif"];
	mimeType         = "image/jpeg";
	magic            = ["JFIF JPEG bitmap", "JPEG image data", "JPEG bitmap", "JPEG File Interchange Format", "JFIF-EXIF JPEG Bitmap", /^fmt\/(43|44)( |$)/];
	fallback         = true;	// Some other formats such as image/a4r can be mistaken for JPEG data by 'file' command, so we ensure we try other formats first before falling back to this
	confidenceAdjust = () => 25;	// Adjust confidence so it's above fileSize matches, since being an image many things can convert with the same tools
	untouched        = dexState => dexState.meta.width && dexState.meta.height;
	verifyUntouched  = dexState => dexState.meta.format!=="JPEG";
	metaProvider     = ["image"];
	converters       = ["imageAlchemy"];	// some jpgs are corrupt but imageAlchemy seems to be very flexible and can handle them
}
