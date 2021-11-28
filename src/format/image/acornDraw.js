import {Format} from "../../Format.js";

export class acornDraw extends Format
{
	name       = "Acorn/RISC-OS Draw";
	website    = "http://fileformats.archiveteam.org/wiki/Acorn_Draw";
	magic      = ["RISC OS Draw file data", "Acorn Draw vector image"];
	converters = ["drawview"];
}
