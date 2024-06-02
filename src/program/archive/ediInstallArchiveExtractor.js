import {Program} from "../../Program.js";

export class ediInstallArchiveExtractor extends Program
{
	website   = "http://cd.textfiles.com/cica/cica9603/disk1/disc1/util/wramp12.zip";
	loc       = "dos";
	bin       = "EDIXTRCT/EXTRACT.EXE";
	args      = r => [`/U:${r.outDir({backslash : true})}`, r.inFile({backslash : true})];
	renameOut = true;
}
