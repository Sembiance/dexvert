import {Format} from "../../Format.js";

export class corelDrawPattern extends Format
{
	name           = "Corel Draw Pattern";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = ["CorelDRAW Pattern", "RIFF Datei: unbekannter Typ 'cdr6'", "Generic RIFF file cdr6", "Generic RIFF file CDR4", "deark: riff (CorelDRAW (RIFF-based))", "Corel Draw bitmap :cpat:", /Corel Draw Pattern/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="CPAT" && macFileCreator==="Cdrw";
	notes          = "Only the preview image is supported at the moment.";
	converters     = ["nconvert[format:cpat]", "deark[module:riff]"];
}
