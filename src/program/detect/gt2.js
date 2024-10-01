import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {path} from "std";

export class gt2 extends Program
{
	website   = "https://www.helger.com/gt/gt2.htm";
	loc       = "wine";
	bin       = "c:\\Program Files\\GT2\\gt2.exe";
	args      = r => ["/noarcs", "/nu", "/noerrbox", "/nologo", "/nocolor", "/noscanname", "/noscanext", "/outlinenums", `c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`];
	
	// can't run more than 1 copy at a time, it messes up. Can test this by running this over and over: ./testdexvert --format=text/microsoftMapData
	// tried adding a preCopyDir feature (see sandbox/legacy/wineUtil-preCopyDir.js) where each instance is ran in it's own directory, but that didn't help, so it must be using like a common registry or something
	exclusive = "gt2";

	wineData  = {
		keepOutput : true,
		timeout    : xu.SECOND*2	// since we are only running 1 at a time, ensure it doesn't take took long to run and hang up everything else
	};
	post = r =>
	{
		const matchValues = (r.status?.stdout || "").split("\n").map(line => line.match(/^3: (?<magic>.+)/)?.groups.magic).filter(v => !!v);
		r.meta.detections = (matchValues.length!==1 || !matchValues[0].length || matchValues[0].startsWith("Fehler:")) ? [] : [Detection.create({value : `${matchValues[0]}`, from : "gt2", file : r.f.input})];
	};
	renameOut = false;
}
