import {Format} from "../../Format.js";

export class jpg extends Format
{
	name             = "Joint Photographic Experts Group Image";
	website          = "http://fileformats.archiveteam.org/wiki/JPG";
	ext              = [".jpg", ".jpeg", ".jpe", ".jfif"];
	mimeType         = "image/jpeg";
	magic            = ["JFIF JPEG bitmap", "JPEG image data", "JPEG bitmap", "JPEG File Interchange Format", "JFIF-EXIF JPEG Bitmap", "Macintosh JPEG bitmap (MacBinary)", /^fmt\/(41|42|43|44)( |$)/];
	fallback         = true;	// Some other formats such as image/a4r can be mistaken for JPEG data by 'file' command, so we ensure we try other formats first before falling back to this
	confidenceAdjust = () => 25;	// Adjust confidence so it's above fileSize matches, since being an image many things can convert with the same tools
	untouched        = dexState => dexState.meta.width && dexState.meta.height;
	verifyUntouched  = dexState => dexState.meta.format!=="JPEG";
	metaProvider     = ["image"];
	converters       = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Macintosh JPEG bitmap (MacBinary)"))
			r.push("deark[mac][convertAsExt:.jpg]");
		r.push("imageAlchemy", "pv[matchType:magic]");	// some jpgs are corrupt (image5.jpg, mpfeif07.jpg, ring_mo4.jpg) but imageAlchemy/pv are flexible and can handle them
		return r;
	};
}
