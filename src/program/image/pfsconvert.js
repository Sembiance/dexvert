import {Program} from "../../Program.js";

export class pfsconvert extends Program
{
	website        = "http://pfstools.sourceforge.net/";
	gentooPackage  = "media-gfx/pfstools";
	gentooUseFlags = "fftw gsl imagemagick netpbm openexr opengl qt5 tiff";
	gentooOverlay  = "dexvert";
	bin            = "pfsconvert";
	args           = async r => [r.inFile(), await r.outFile("out.png")];
}
