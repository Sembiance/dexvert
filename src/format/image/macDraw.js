import {Format} from "../../Format.js";

export class macDraw extends Format
{
	name           = "MacDraw";
	website        = "http://fileformats.archiveteam.org/wiki/MacDraw";
	ext            = [".pict", ".drw"];
	forbidExtMatch = true;
	magic          = ["MacDraw drawing", /^fmt\/(1425|1426|1427|1428)( |$)/];
	idMeta         = ({macFileType}) => macFileType==="DRWG";
	metaProvider   = ["image"];
	converters     = [
		// soffice handles it the best, especially with files: grundriss & ][_-_Mac cable (print me!)
		"soffice[outType:png]"

		// deark and nconvert will both 'seemingly' convert MacDraw files, but what they are really doing is extracting embedded PICT files from within them
		// in many cases this appears to work just fine, but it fails with the files mentioend above for soffice
	];
}
