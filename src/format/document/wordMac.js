import {Format} from "../../Format.js";

export class wordMac extends Format
{
	name       = "Macintosh Word Document";
	website    = "http://fileformats.archiveteam.org/wiki/Microsoft_Word_for_Macintosh";
	magic      = ["Word for the Macintosh", "Microsoft Word for Macintosh", "Microsoft Word document (MacBinary)", "Mac Microsoft Word document (MacBinary)", /^x-fmt\/(1|64|65)( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => (["GLOS", "W6BN", "WDBN", "WTBN"].includes(macFileType) && ["MSWD", "MSWT"].includes(macFileCreator)) ||
		"WORD".includes(macFileType) ||
		(macFileType==="WDBN" && macFileCreator==="WORD");
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Microsoft Word document (MacBinary)") || dexState.hasMagics("Mac Microsoft Word document (MacBinary)"))
			r.push("deark[module:macbinary][mac][deleteADF] -> soffice");
		r.push("soffice[format:Mac Word]", "keyViewPro[outType:pdf]");
		return r;
	};
}
