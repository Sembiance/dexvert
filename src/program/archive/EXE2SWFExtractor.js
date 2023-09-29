import {xu} from "xu";
import {Program} from "../../Program.js";

export class EXE2SWFExtractor extends Program
{
	website  = "https://sothink.com/product/flashdecompiler/";
	unsafe   = true;
	loc      = "winxp";
	bin      = "EXE2SWFExtractor.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			WinWaitActive("Sothink EXE to SWF Extractor", "", 10)

			Sleep(250)

			ControlSetText("Sothink EXE to SWF Extractor", "", "[CLASS:Edit; INSTANCE:1]", "c:\\out")

			ControlClick("Sothink EXE to SWF Extractor", "", "[CLASS:Button; TEXT:Extract]")

			WaitForControl("Sothink EXE to SWF Extractor", "", "[CLASS:Button; TEXT:OK]", ${xu.SECOND*20})

			ControlClick("Sothink EXE to SWF Extractor", "", "[CLASS:Button; TEXT:OK]")

			WaitForPID("EXE2SWFExtractor.exe", ${xu.SECOND*10})`
	});
	chain     = "dexvert";
	renameOut = true;
}
