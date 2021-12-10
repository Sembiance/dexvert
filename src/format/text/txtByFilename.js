/*import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class txtByFilename extends Format
{
	name             = "Text File";
	website          = "http://fileformats.archiveteam.org/wiki/Text";
	magic            = [...TEXT_MAGIC, /^data$/];
	weakMagic        = true;
	forbidMagicMatch = true;
	priority         = this.PRIORITY.VERYLOW;
	filename         = [
		/registra.tio/i, /register.* /i,	// TODO I put a space before the forward slash, undo that
		/descript.ion/i,
		/file_id.*\.diz/i,
		/^disk_ord.er.?$/i, /ordrform/i,
		/^(about|change|copying|description|manifest|manual|order|problems|readme|readnow|readthis|release|todo|whatsnew)[._-]*($|\..+$)/i,
		/^.*read\..*me.*$/i, /^.*read.*me.*\./i, /^.*read.?me.?$/i, /^read.*me.*$/i, /^.read_this/i, /^whats\.new$/i,
		/^.*manu.al$/i,
		/[_-]te?xt$/i
	];
	weakFilename = true;
	
	untouched = true;
	fallback  = true;

	// TODO the below
	//inputMeta = p.family.supportedInputMeta(state, p, cb)
}
*/
