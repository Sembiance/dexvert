import {Format} from "../../Format.js";

export class hyperTerminalDataFile extends Format
{
	name           = "HyperTerminal Data File";
	ext            = [".ht"];
	forbidExtMatch = true;
	magic          = ["HyperTerminal data file"];
	converters     = ["strings[minBytes:3]"];	// 3 bytes minimum will esure the prefix number of the telephone number is extracted
}
