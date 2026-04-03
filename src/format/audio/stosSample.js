import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class stosSample extends Format
{
	name           = "STOS Sample";
	website        = "https://en.wikipedia.org/wiki/STOS_BASIC";
	ext            = [".sam"];
	forbidExtMatch = true;
	magic          = ["STOS Sample"];
	idCheck        = async inputFile => inputFile.size>4 && (await fileUtil.readFileBytes(inputFile.absolute, 4))[3]<0x41;
	converters     = ["vibe2wav[renameOut]"];
}
