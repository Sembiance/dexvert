import {Format} from "../../Format.js";

export class cardfile extends Format
{
	name       = "Cardfile Document";
	website    = "http://fileformats.archiveteam.org/wiki/Cardfile";
	ext        = [".crd"];
	magic      = ["Windows Cardfile database", "Cardfile"];
	converters = ["deark & cardfile"];
}
