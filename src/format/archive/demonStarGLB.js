import {Format} from "../../Format.js";

export class demonStarGLB extends Format
{
	name           = "Demon Star GLB Archive";
	ext            = [".glb"];
	forbidExtMatch = true;
	magic          = [/^geArchive: GLB_GLB2( |$)/];
	converters     = ["gameextractor[codes:GLB_GLB2]"];
}
