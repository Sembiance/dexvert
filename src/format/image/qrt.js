import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";
import {fileUtil} from "xutil";

export class qrt extends Format
{
	name           = "QRT Ray Tracer Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/QRT_Ray_Tracer_bitmap";
	ext            = [".qrt", ".dis", ".raw"];
	forbiddenMagic = ["KryoFlux raw stream", ...TEXT_MAGIC];
	priority       = this.PRIORITY.LOWEST;	// Because we have no magic
	converters     = ["qrttoppm"];	// nconvert and tomsViewer also handle these, but they will take almost anything and produce garbage. qrttoppm does some sanity checks at least snce we don't have magic for this
	verify         = async ({inputFile, meta}) =>
	{
		// Since this format has no magic and can match against .raw extension and convert garbage, we need to do some sanity checks
		if(meta.height<11 || meta.width<11)	// This is a ray tracing format and it's unlikely to produce anything this small
			return false;

		const header = await fileUtil.readFileBytes(inputFile.absolute, 6);
		// 2 bytes width  2 bytes height  2 bytes row 0 prefix
		if(meta.width!==header.getUInt16LE(0) || meta.height!==header.getUInt16LE(2) || header.getUInt16LE(4)!==0)
			return false;

		return true;
	};
}
