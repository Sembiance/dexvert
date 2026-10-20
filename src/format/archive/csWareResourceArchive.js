import {Format} from "../../Format.js";

export class csWareResourceArchive extends Format
{
	name           = "C's ware Resource Archive";
	ext            = [".dl1", ".r1", ".r2", ".r3", ".r4"];
	forbidExtMatch = true;
	magic          = ["archive:Csware.Dl1Opener"];
	converters     = ["GARbro[types:archive:Csware.Dl1Opener]"];
}
