import {Format} from "../../Format.js";

export class qrt extends Format
{
	name           = "QRT Ray Tracer Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/QRT_Ray_Tracer_bitmap";
	ext            = [".qrt", ".dis", ".raw"];
	forbiddenMagic = ["KryoFlux raw stream"];
	converters     = ["nconvert", "tomsViewer"];
}
