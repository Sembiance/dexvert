import {Format} from "../../Format.js";

export class industryFoundationClasses extends Format
{
	name           = "Industry Foundation Classes";
	website        = "http://fileformats.archiveteam.org/wiki/IFC";
	ext            = [".ifc"];
	forbidExtMatch = true;	// too modern, unlikely to match
	magic          = [/^fmt\/700( |$)/];
	converters     = ["assimp"];
}
