import {Format} from "../../Format.js";

export class rtcwMDC extends Format
{
	name           = "Return to Castle Wolfenstein MDC";
	website        = "https://mino-git.github.io/rtcw-wet-blender-model-tools/publications/MDCFileFormat.pdf";
	ext            = [".mdc"];
	forbidExtMatch = true;
	magic          = ["rtcwMDC"];
	converters     = ["assimp", "milkShape3D[format:rtcwMDC]"];
}
