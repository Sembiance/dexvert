import {Program} from "../../Program.js";

export class guideml extends Program
{
	website   = "http://aminet.net/package/text/hyper/guideml";
	unsafe    = true;
	loc       = "amiga";
	notes     = "No longer used, due to being very buggy and hangs on almost anything";
	bin       = "GuideML_OS4";
	args      = r => ["FILE", r.inFile(), "TO", "HD:out/"];
	osData    = ({noAuxFiles : true});
	renameOut = false;
}
