import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class man2html extends Program
{
	website    = "http://primates.ximian.com/~flucifredi/man/";
	package    = "sys-apps/man2html";
	bin        = "man2html";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.html")});
	verify     = async (r, dexFile) => dexFile.size<(xu.MB*10) && !(await Deno.readTextFile(dexFile.absolute)).includes("<H1>Invalid Manpage</H1>");
	renameOut  = true;
	post       = async r => (r.f.new ? (await fileUtil.searchReplace(r.f.new.absolute, "Content-type: text/html", "")) : "");
}
