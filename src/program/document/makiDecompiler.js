import {Program} from "../../Program.js";

export class makiDecompiler extends Program
{
	website    = "https://web.archive.org/web/20131020030559/http://www.rengels.de/maki_decompiler/download.html";
	bin        = Program.binPath("maki_decompiler_1.1/mdc.pl");
	args       = r => [r.inFile({absolute : true})];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out", {absolute : true}), cwd : Program.binPath("maki_decompiler_1.1")});
	renameOut  = true;
}
