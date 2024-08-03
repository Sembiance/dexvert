import {Format} from "../../Format.js";

export class turboCADDrawing extends Format
{
	name       = "TurboCAD Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/TCW";
	ext        = [".tcw"];
	magic      = ["TurboCAD drawing", "KeyCAD Deluxe for Windows drawing", "KeyCAD Deluxe for Windows symbol"];
	converters = ["turboCAD"];
}
