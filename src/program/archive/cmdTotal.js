import {xu} from "xu";
import {Program} from "../../Program.js";

export class cmdTotal extends Program
{
	website = "https://totalcmd.net/plugring/cmdtotal.html";
	loc     = "wine";
	flags   = {
		wcx : "Which wcx file to use"
	};
	bin       = "c:\\dexvert\\cmdTotal\\cmdTotal.exe";
	args      = r => [r.flags.wcx, "x", r.inFile(), r.outDir()];
	renameOut = false;
}

/* WCX plugins installed:
Name					WCX File		Notes									Website
----					--------		-----									-------
InstallExplorer 0.9.2 	InstExpl.wcx	Handles various installer packages		https://totalcmd.net/plugring/installexplorer.html

More available from: https://totalcmd.net/directory/packer.html
*/
