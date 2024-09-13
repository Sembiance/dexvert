import {Format} from "../../Format.js";

export class corelClipart extends Format
{
	name       = "Corel Clipart";
	website    = "http://fileformats.archiveteam.org/wiki/CCX_(Corel)";
	ext        = [".ccx", ".cdr"];
	priority   = this.PRIORITY.HIGH;	// this ensures we rank higher than image/cdr for things like sample/image/corelClipart/homer1.cdr
	magic      = ["Corel Clipart", "RIFF Datei: unbekannter Typ 'CDRX'", /^RIFF.+Corel Clipart/];
	converters = ["uniconvertor[autoCrop]", "deark[module:corel_ccx][renameOut] -> dexvert[asFormat:image/cmx]", "nconvert"];
}
