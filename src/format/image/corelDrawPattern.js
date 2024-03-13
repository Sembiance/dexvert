import {Format} from "../../Format.js";

export class corelDrawPattern extends Format
{
	name           = "Corel Draw Pattern";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = ["CorelDRAW Pattern", "RIFF Datei: unbekannter Typ 'cdr6'", /Corel Draw Pattern/];
	notes          = "Only the preview image is supported at the moment.";
	converters     = ["deark[module:riff]"];
}
