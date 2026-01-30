import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";
import {fileUtil} from "xutil";

export class sixel extends Format
{
	name         = "Sixel";
	website      = "http://fileformats.archiveteam.org/wiki/Sixel";
	ext          = [".six", ".sixel"];
	mimeType     = "image/x-sixel";
	magic        = TEXT_MAGIC;
	weakMagic    = true;
	idCheck = async inputFile =>
	{
		const headerBuf = await fileUtil.readFileBytes(inputFile.absolute, Math.min(150, inputFile.size));
		return headerBuf.indexOfX([0x1B, 0x50])!==-1 || headerBuf.indexOfX([0x1B, 0x5B])!==-1 || headerBuf.indexOfX([0x90])===0;
	};
	metaProvider = ["image"];
	converters   = ["sixel2png", "convert[format:SIXEL]", "wuimg[format:sixel]", `abydosconvert[format:${this.mimeType}]`];
	verify       = ({meta}) => meta.colorCount>1;
}
