import {xu} from "xu";
import {Program} from "../../Program.js";

export class amigadepacker extends Program
{
	website    = "http://zakalwe.fi/~shd/foss/amigadepacker/";
	package    = "app-arch/amigadepacker";
	bin        = "amigadepacker";
	args       = async r => ["-o", await r.outFile("out"), r.inFile()];
	runOptions = ({timeout : xu.SECOND*20});	// If you pass it a password protected file such as archive/powerPack/013 it will brute force the password which takes AGES. So just stop after 20 seconds
	renameOut  = true;
}
