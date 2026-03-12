import {Format} from "../../Format.js";

export class vxbgArchive extends Format
{
	name           = "VXBG Archive";
	ext            = [".vbf", ".syb", ".sl"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SL_VXBG( |$)/];
	converters     = ["gameextractor[codes:SL_VXBG]"];
}
