import {Format} from "../../Format.js";

export class epocExecutable extends Format
{
	name           = "EPOC/Symbian Executable";
	website        = "http://fileformats.archiveteam.org/wiki/EPOC/Symbian_executable";
	ext            = [".app", ".opx", ".opo", ".opl", ".dll"];
	forbidExtMatch = true;
	magic          = ["Psion Series 5 OPL application", "EPOC/Symbian OPL Application", "EPOC OPL Object module", "Psion Series 5 OPO module"];
	converters     = ["strings"];
}
