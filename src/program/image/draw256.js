import {Program} from "../../Program.js";

export class draw256 extends Program
{
	website = "http://cd.textfiles.com/megarom/megarom3/GRAPHICS/APPS/DRAWV221.ZIP";
	unsafe  = true;
	loc     = "dos";
	bin     = "DRAW256/DRAW256.EXE";
	args    = r => [`..\\..\\${r.f.input.rel.replaceAll("/", "\\")}`]
	dosData = r => ({runIn : "prog", keys : ["s", `..\\..\\${r.f.outDir.rel.replaceAll("/", "\\")}\\F.PCX`, ["Return"], ["Escape"], "y"]});
	chain   = "dexvert[asFormat:image/pcx]";
}
