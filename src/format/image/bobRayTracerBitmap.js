import {Format} from "../../Format.js";

export class bobRayTracerBitmap extends Format
{
	name       = "Bob Ray Tracer Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Bob_ray_tracer_bitmap";
	ext        = [".bob"];
	magic      = ["deark: bob", "Bob :bob:"];
	weakMagic  = true;
	converters = ["deark", "nconvert[format:bob]", "wuimg[matchType:magic]", "tomsViewer[matchType:magic]"];	// do NOT specify [module:bob] for deark as we just have a ext match and specyfing the module bypasses some sanity checking that deark does which causes too many false positives
}
