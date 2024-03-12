import {xu} from "xu";
import {Program} from "../../Program.js";

export class ogreXMLConveter129 extends Program
{
	website  = "https://codeberg.org/Kindrad/Kenshi_IO_Continued/src/branch/main/XML_1_29";
	loc      = "wine";
	bin      = "ogreXMLConveter129/OgreXMLConverter.exe";
	args     = async r => [r.inFile(), await r.outFile("out.mesh.xml")];
	wineData = ({
		base : "win64",
		arch : "win64"
	});
	renameOut = true;
}


