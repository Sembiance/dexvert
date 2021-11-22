import {Program} from "../../Program.js";

export class autoCropSVG extends Program
{
	website        = "https://inkscape.org/";
	gentooPackage  = "media-gfx/inkscape";
	gentooUseFlags = "cdr dbus dia exif graphicsmagick jpeg openmp postscript visio wpg";

	bin  = "inkscape";
	args = r => ["-g", "--batch-process", "--verb", "FitCanvasToDrawing;FileSave;FileClose", r.inFile()];
	runOptions = ({virtualX : true});
}
