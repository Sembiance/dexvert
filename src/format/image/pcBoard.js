import {Format} from "../../Format.js";

export class pcBoard extends Format
{
	name             = "PC-Board";
	website          = "http://fileformats.archiveteam.org/wiki/PCBoard";
	ext              = [".pcb"];
	forbidExtMatch   = true;
	mimeType         = "text/x-pcboard";
	magic            = [/^data$/, "ISO-8859 text"];
	weakMagic        = true;
	forbiddenMagic   = ["PCB 3.0 Binary file", "P-CAD Printed Curcuit Board"];
	confidenceAdjust = () => -70;	// Reduce by 70 so that pretty much everything else matches first, since I can only match really to extension and ansilove will convert almost anything
	metaProvider     = ["ansiloveInfo"];
	
	// We do NOT use abydos, because it just falls back to ansilove
	converters = ["ansilove"];
}
