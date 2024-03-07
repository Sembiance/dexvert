import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {path} from "std";

export class gt2 extends Program
{
	website = "https://www.helger.com/gt/gt2.htm";
	loc     = "wine";
	bin     = "c:\\Program Files\\GT2\\gt2.exe";
	args    = r => ["/noarcs", "/nu", "/noerrbox", "/nologo", "/nocolor", "/noscanname", "/noscanext", "/outlinenums", `c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`];
	wineData = {
		keepOutput : true
	};
	post    = r =>
	{
		const matchValues = r.status.stdout.split("\n").map(line => line.match(/^3: (?<magic>.+)/)?.groups.magic).filter(v => !!v);
		r.meta.detections = (matchValues.length!==1 || !matchValues[0].length || matchValues[0].startsWith("Fehler:")) ? [] : [Detection.create({value : `${matchValues[0]}`, from : "gt2", file : r.f.input})];
	};
	renameOut = false;
}
// /outlinenums
// /l
// /bufsize8192
