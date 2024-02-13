import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";
import {fileUtil} from "xutil";

export class avatar extends Format
{
	name           = "Avatar/0";
	website        = "http://fileformats.archiveteam.org/wiki/AVATAR";
	ext            = [".avt"];
	// So .avt of course can match anything, and sadly abydosconvert will convert almost anything in garbage.
	// I scoured many avatar samples and they all have a combination of 0x16 0x?? in the beginning of the file, so we'll use that as an extra check
	idCheck = async inputFile =>
	{
		const headerBuf = await fileUtil.readFileBytes(inputFile.absolute, Math.min(50, inputFile.size));
		return [[0x16, 0x01], [0x16, 0x05], [0x16, 0x06], [0x16, 0x08]].some(bytes => headerBuf.indexOfX(bytes)!==-1);
	};
	mimeType       = "text/x-avatar0";
	forbiddenMagic = TEXT_MAGIC_STRONG;
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}
