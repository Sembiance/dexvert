import {Format} from "../../Format.js";

export class madStudio extends Format
{
	name        = "Mad Studio";
	website     = "http://fileformats.archiveteam.org/wiki/Mad_Studio";
	ext         = [".gr1", ".gr2", ".gr3", ".gr0", ".mpl", ".msl", ".spr", ".an2", ".an4", ".an5", ".tl4"];
	converters  = ["recoil2png[format:TL4,AN2,GR1,MPL,AN4,GR3,MSL,GR2,AN5,ASC,GR0]"];
	unsupported = true;	// only recognized by extension and is a modern format from 2016
}
