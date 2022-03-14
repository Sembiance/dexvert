import {Format} from "../../Format.js";

export class portableFontResource extends Format
{
	name        = "Portable Font Resource";
	website     = "http://fileformats.archiveteam.org/wiki/PFR";
	ext         = [".pfr"];
	magic       = ["Portable Font Resource", "Portable Font Resource font data"];
	notes       = "Could create a custom HTML file that references the PFR and load it in Netscape 4.03 and take a screenshot.";
	unsupported = true;
}
