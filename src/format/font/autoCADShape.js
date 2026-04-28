import {Format} from "../../Format.js";

export class autoCADShape extends Format
{
	name           = "AutoCAD Shape/Font";
	ext            = [".shx"];
	forbidExtMatch = true;
	magic          = ["AutoCAD Shape", "AutoCAD Compiled Shape", /^x-fmt\/103( |$)/];
	converters     = ["vibe2svg[skipVerify]"];
}
