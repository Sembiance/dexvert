import {Program} from "../../Program.js";

export class webpinfo extends Program
{
	website        = "https://developers.google.com/speed/webp/download";
	gentooPackage  = "media-libs/libwebp";
	gentooUseFlags = "gif jpeg opengl png tiff";
	bin = "webpinfo";
	args = r => [r.inFile()];
	post = r =>
	{
		if(r.stdout.trim().includes("Animation: 1"))
			r.meta.animated = true;
	}
}
