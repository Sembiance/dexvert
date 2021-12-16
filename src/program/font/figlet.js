import {Program} from "../../Program.js";

export class figlet extends Program
{
	website    = "http://www.figlet.org/";
	package    = "app-misc/figlet";
	bin        = "figlet";
	args       = r => ["-f", r.inFile(), `abcdefghijklmnopqrstuvwxyz\nABCDEFGHIJKLMNOPQRSTUVWXYZ\n0123456789\n\`~!@#$%^&*()-_+=>;,<;.[]{}|\\:;"'/?`];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}

