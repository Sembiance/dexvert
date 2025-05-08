import {Format} from "../../Format.js";

export class corelSHOW extends Format
{
	name       = "CorelSHOW Presentation";
	website    = "http://fileformats.archiveteam.org/wiki/SHW_(Corel)";
	ext        = [".shw"];
	magic      = ["CorelSHOW presentation", /^RIFF Datei: unbekannter Typ 'shw\d'/, /^Generic RIFF file shw\d/];
	notes      = "Deark only capable of extracting the thumbnail images for each slide using RIFF module. CorelSHOW worked on Win2k and played these, but I saw no easy way to export all slides.";
	converters = ["deark[module:riff]"];
}
