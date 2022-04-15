import {xu} from "xu";
import {Program} from "../../Program.js";

export class pycdc extends Program
{
	website = "https://github.com/zrax/pycdc";
	package = "dev-util/pycdc";
	bin     = "pycdc";
	args    = r => [r.inFile()];
	
	// some files like urllib.pyo just run forever and output an infinite loop of stuff. So limit disk space, runtime and only approve if it didn't timeout
	diskQuota  = xu.MB*5;
	runOptions = async r => ({timeout : xu.SECOND*10, stdoutFilePath : await r.outFile("out.py")});
	verify     = r => r.status.success;
	renameOut  = true;
}
