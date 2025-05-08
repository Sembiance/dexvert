import {Format} from "../../Format.js";

export class acornDraw extends Format
{
	name        = "Acorn/RISC-OS Draw";
	website     = "http://fileformats.archiveteam.org/wiki/Acorn_Draw";
	magic       = ["RISC OS Draw file data", "Acorn Draw vector image"];
	converters  = ["drawview"];
	unsupported = true;	// TODO: Need to update drawview to work without pulling in KDE crap. See: https://github.com/martenjj/drawview/issues/7
}
