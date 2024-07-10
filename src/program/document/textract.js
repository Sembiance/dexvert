import {xu} from "xu";
import {Program} from "../../Program.js";

export class textract extends Program
{
	website   = "https://archive.org/details/msdos_shareware_fb_TXT2EXE";
	loc       = "dos";
	bin       = "TEXTRACT.EXE";
	args      = r => [r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out", keys : [{delay : xu.SECOND*3}, ["Enter"]]});
	renameOut = {alwaysRename : true, renamer : [({newName}) => ([newName, ".txt"])]};
}
