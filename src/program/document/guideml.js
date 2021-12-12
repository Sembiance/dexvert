import {Program} from "../../Program.js";

export class guideml extends Program
{
	website = "http://aminet.net/package/text/hyper/guideml";
	unsafe  = true;
	loc     = "amigappc";
	// GuideML can just hang forever, or crash, but both cases seem to be handled ok by the supervisor.rexx script and it's internal 180.0 second (3 minutes) timeout
	bin       = "GuideML_OS4";
	args      = r => ["FILE", r.inFile(), "TO", "HD:out/"];
	qemuData  = ({noAuxFiles : true});
	renameOut = false;
}
