import {Program} from "../../Program.js";

export class cabextract extends Program
{
	website   = "https://www.cabextract.org.uk/";
	package   = "app-arch/cabextract";
	bin       = "cabextract";
	args      = r => ["--directory", r.outDir(), "--fix", r.inFile()];
	renameOut = false;
}
