import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class qrt extends Format
{
	name           = "QRT Ray Tracer Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/QRT_Ray_Tracer_bitmap";
	ext            = [".qrt", ".dis", ".raw"];
	forbiddenMagic = ["KryoFlux raw stream", ...TEXT_MAGIC];
	priority       = this.PRIORITY.LOWEST;	// Because we have no magic
	converters     = ["qrttoppm"];	// nconvert and tomsViewer also handle these, but they will take almost anything and produce garbage. qrttoppm does some sanity checks at least snce we don't have magic for this
	verify         = ({meta}) => meta.height>1 && meta.width>1;
}
