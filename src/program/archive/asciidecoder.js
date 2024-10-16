import {Program} from "../../Program.js";

export class asciidecoder extends Program
{
	website   = "https://github.com/fzipp/oberon/blob/main/cmd/asciidecoder/main.go";
	package   = "app-arch/asciidecoder";
	bin       = "asciidecoder";
	cwd       = r => r.outDir();
	args      = r => [r.inFile()];
	renameOut = false;
}
