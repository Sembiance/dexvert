import {Program} from "../../Program.js";

export class draw256 extends Program
{
	website = "http://cd.textfiles.com/megarom/megarom3/GRAPHICS/APPS/DRAWV221.ZIP";
	unsafe  = true;
	loc     = "dos";
	bin     = "DRAW256/DRAW256.EXE";
	args    = r => [`..\\..\\${r.inFile({backslash : true})}`]
	dosData = async r => ({runIn : "prog", keys : ["s", `..\\..\\${await r.outFile("F.PCX", {backslash : true})}`, ["Return"], ["Escape"], "y"]});
	chain   = "dexvert[asFormat:image/pcx]";
}
