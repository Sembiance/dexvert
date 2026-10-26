import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

const _AUX_EXTS = [".icn", ".ic1", ".ic4", ".ic5", ".ic6"];

export class ripScrip extends Format
{
	name         = "Remote Imaging Protocol Script";
	website      = "http://fileformats.archiveteam.org/wiki/RIPscrip";
	ext          = [".rip"];
	mimeType     = "image/x-rip-scrip";
	magic        = ["RIPscript", "ANSI escape sequence text"];
	weakMagic    = ["ANSI escape sequence text"];
	idCheck      = async inputFile => (await fileUtil.readFileBytes(inputFile.absolute, Math.min(32, inputFile.size))).indexOfX([0x21, 0x7C])!==-1;
	auxFiles     = (input, otherFiles) => (otherFiles?.some(file => _AUX_EXTS.includes(file.ext.toLowerCase())) ? otherFiles.filter(file => _AUX_EXTS.includes(file.ext.toLowerCase())) : false);
	keepFilename = true;
	converters   = ["vibe2svg[multiple][renameOut]", "pabloDraw", `abydosconvert[format:${this.mimeType}]`];
}
