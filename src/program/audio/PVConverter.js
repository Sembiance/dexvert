import {Program} from "../../Program.js";

export class PVConverter extends Program
{
	website   = "https://web.archive.org/web/20101229181642/http://www.qualcomm.com/products_services/mobile_content_services/voice/purevoice.html";
	package   = "media-sound/PVConverter";
	bin       = "pvconv";
	args      = async r => [r.inFile(), await r.outFile("out.wav")];
	renameOut = true;
	chain     = "sox";
}
