import {Format} from "../../Format.js";

export class hrs extends Format
{
	name           = "Oric Hires Screen";
	website        = "http://fileformats.archiveteam.org/wiki/Oric_HIRES_screen;";
	ext            = [".hrs", ".hir", ".tap"];
	forbidExtMatch = [".tap"];
	magic          = ["Oric Tape Image", "Hires Oric :otap:"];
	weakMagic      = true;
	converters     = ["recoil2png"];	// "nconvert[format:otap]" works for zoolymp.tap and kinda works for bounce/graph/loki/shuttle/sorvivor/tennis/tricksht but for all else it just outputs garbage: https://discmaster.textfiles.com/browse/11986/2007-01-13_www.messroms.de.zip/ORIC1/IMAGES
}
