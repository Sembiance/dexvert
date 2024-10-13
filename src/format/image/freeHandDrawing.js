import {Format} from "../../Format.js";

export class freeHandDrawing extends Format
{
	name       = "FreeHand Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/FreeHand";
	ext        = [".fh", ".fh2", ".fh3", ".fh4", ".fh5", ".fh6", ".fh7", ".fh8", ".fh9", ".fh10"];
	magic      = ["FreeHand drawing", /^Freehand (\d+)?\(MX\) Project/, /^Macromedia Freehand.*Document/, /^fmt\/(400|544|545|546|547|1449|1450)( |$)/, /^x-fmt\/(303|304)( |$)/];
	idMeta     = ({macFileType}) => macFileType==="FHD3";
	converters = ["soffice[outType:svg][autoCropSVG]", "scribus"];	// These are often centered on a huge blank canvas, so autoCropSVG will take care of that
}
