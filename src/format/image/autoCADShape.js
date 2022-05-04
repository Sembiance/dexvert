import {Format} from "../../Format.js";

export class autoCADShape extends Format
{
	name        = "AutoCAD Shape";
	ext         = [".shx"];
	magic       = ["AutoCAD Shape", /^x-fmt\/103( |$)/];
	unsupported = true;
}
