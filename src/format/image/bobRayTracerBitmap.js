import {Format} from "../../Format.js";

export class bobRayTracerBitmap extends Format
{
	name       = "Bob Ray Tracer Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Bob_ray_tracer_bitmap";
	ext        = [".bob"];
	converters = [
		"deark",	// don't specify module:bob because we don't have a strong enough match
		"nconvert", "tomsViewer"
	];
}
