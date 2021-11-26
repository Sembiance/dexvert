import {Program} from "../../Program.js";

export class ezdxf extends Program
{
	website       = "https://ezdxf.mozman.at/";
	gentooPackage = "dev-python/ezdxf";
	gentooOverlay = "dexvert";
	unsafe        = true;
	bin           = "ezdxf";
	args          = async r => ["draw", "-o", await r.outFile("out.svg"), r.inFile()];
	chain         = "deDynamicSVG";
}
