import {Format} from "../../Format.js";

export class renPyArchive extends Format
{
	name           = "Ren'Py Archive";
	ext            = [".rpa"];
	forbidExtMatch = true;
	magic          = ["Ren'Py Archive", "archive:RenPy.RpaOpener"];
	weakMagic      = true;
	converters     = ["GARbro[types:archive:RenPy.RpaOpener]"];
}
