import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffTDDD extends Format
{
	name       = "TDDD TurboSilver/Imagine 3D Object";
	website    = "http://fileformats.archiveteam.org/wiki/TDDD";
	ext        = [".iob", ".tdd", ".cel", ".obj"];
	magic      = ["IFF data, TDDD 3-D rendering", "3D Data Description object", "Impulse 3D Data Description Object", /^fmt\/1206( |$)/];
	converters = ["AccuTrans3D", "blender[format:tddd]", "cinema4D427", "threeDObjectConverter"];
	notes      = xu.trim`The import script does not handle many of the tags from the TDDD format (Spitfire.iob). An initial stab at handling some of the color info (CLST, RLST, TLST) didn't provide any results (see sandbox/legacy/blender/io_import_scene_tddd.py)`;
}
