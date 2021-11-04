import {Format} from "../../Format.js";

export class jpg extends Format
{
	name      = "Joint Photographic Experts Group Image";
	website   = "http://fileformats.archiveteam.org/wiki/JPG";
	ext       = [".jpg", ".jpeg", ".jpe", ".jfif"];
	mimeType  = "image/jpeg";
	magic     = ["JFIF JPEG bitmap", "JPEG image data", "JPEG bitmap", "JPEG File Interchange Format"];
	untouched = true;

	//inputMeta = p.family.supportedInputMeta(state, p, cb);
}
