import {Program} from "../../Program.js";
import {path} from "std";

export class guideml extends Program
{
	website   = "http://aminet.net/package/text/hyper/guideml";
	unsafe    = true;
	bin       = "vamos";
	args      = r => [...Program.vamosArgs("GuideML_OS3"), "FILE", r.inFile(), "TO", path.join(r.outDir(), "/")];
	osData    = ({noAuxFiles : true});
	renameOut = false;
}
