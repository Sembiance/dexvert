import {Format} from "../../Format.js";

export class ikuraGDL extends Format
{
	name       = "IKURA GDL Archive";
	magic      = ["archive:Ikura.MpxOpener"];
	converters = ["GARbro[types:archive:Ikura.MpxOpener]"];
}
