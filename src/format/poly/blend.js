import {Format} from "../../Format.js";

export class blend extends Format
{
	name       = "Blender 3D Blend File";
	website    = "http://fileformats.archiveteam.org/wiki/BLEND";
	ext        = [".blend"];
	magic      = ["Blender 3D", "Blender3D", "application/x-blender", "Blender scene description", "Blender :blend:", /^fmt\/(902|903)( |$)/];
	converters = ["blender[format:native]"];
}
