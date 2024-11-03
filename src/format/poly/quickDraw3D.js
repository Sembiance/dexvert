import {xu} from "xu";
import {Format} from "../../Format.js";

export class quickDraw3D extends Format
{
	name       = "QuickDraw 3D Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/3DMF";
	ext        = [".3dmf", ".q3d"];
	magic      = ["QuickDraw 3D Metafile", /^fmt\/(1049|1050|1203)( |$)/];
	idMeta     = ({macFileType}) => macFileType==="3DMF";
	converters = ["polyTrans64[format:quickDraw3D]", "AccuTrans3D"];
	notes      = xu.trim`
		Programs that didn't work:
		Quesa: https://github.com/jwwalker/Quesa 
			Old program, but has recent updates, but still can't build on linux and is just a viewer.
			It could be used as groundwork for a blender or an assimp plugin: https://github.com/assimp/assimp/issues/2362";
		Ayam: https://ayam.sourceforge.net/features.html
			It says it supports 3DMF but only version 1.0. I tried importing a few 3dmf files I have, none of them loaded.`;
}
