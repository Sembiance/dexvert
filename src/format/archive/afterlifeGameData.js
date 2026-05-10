import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class afterlifeGameData extends Format
{
	name           = "Afterlife game data";
	ext            = [".000"];
	forbidExtMatch = true;
	magic          = ["Afterlife game data", /^geArchive: 000_FFIJ( |$)/];
	idCheck        = async inputFile => inputFile.size>4 && new TextDecoder().decode(await fileUtil.readFileBytes(inputFile.absolute, 4))==="FFIJ";
	converters     = ["gameextractor[codes:000_FFIJ]"];
}
