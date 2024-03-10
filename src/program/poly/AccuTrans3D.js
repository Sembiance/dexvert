import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class AccuTrans3D extends Program
{
	website   = "http://www.micromouse.ca/";
	loc       = "win2k";
	bin       = "c:\\dexvert\\AccuTrans3D\\at3d_2012-1-0.exe";
	args      = r => ["-noshow", r.inFile()];
	osData    = r => ({ script : `WaitForStableFileSize("c:\\out\\${path.basename(r.inFile())}.3ds", ${xu.SECOND*3}, ${xu.SECOND*30})` });
	renameOut = true;
	chain     = "dexvert[asFormat:poly/threeDStudio]";
}
