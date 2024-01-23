import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class rawBitmap extends Format
{
	name           = "Raw Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Raw_bitmap";
	ext            = [".raw"];
	forbiddenMagic = ["KryoFlux raw stream", ...TEXT_MAGIC];
	fallback       = true;
	converters     = ["tomsViewer", "nconvert"];
	verify         = ({meta}) => meta.height>1 && meta.width>1;
}
