import {Format} from "../../Format.js";

export class raptorGLBContainer extends Format
{
	name           = "Raptor GLB Container";
	ext            = [".glb", ".gs1", ".gsc"];
	forbidExtMatch = true;
	magic          = ["Raptor GLB encrypted container", /^geArchive: GLB( |$)/];
	converters     = ["gameextractor[codes:GLB]"];
}
