import {Format} from "../../Format.js";

export class kwikDrawDrawing extends Format
{
	name        = "KwikDraw Drawing";
	website     = "http://fileformats.archiveteam.org/wiki/KwikDraw";
	ext         = [".kwk"];
	magic       = ["KwikDraw drawing"];
	converters  = ["kwikDraw", "kwikDraw130"];	// some 1.2.0 files can't be opened in 1.4.0 (kwikDraw) but do work in 1.3.0 (kwikDraw130)
}
