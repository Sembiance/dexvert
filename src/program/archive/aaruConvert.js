import {xu} from "xu";
import {Program} from "../../Program.js";

export class aaruConvert extends Program
{
	website    = "https://github.com/aaru-dps/Aaru";
	package    = "app-arch/Aaru";
	bin        = "aaru";
	args       = async r => ["image", "convert", r.inFile(), await r.outFile("out.cue"), "--force"];
	runOptions = ({env : {DOTNET_ROOT : "/opt/dotnet-sdk-bin-10.0"}});
	renameOut  = false;
}
