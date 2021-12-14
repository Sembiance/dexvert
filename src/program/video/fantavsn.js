import {xu} from "xu";
import {Program} from "../../Program.js";

export class fantavsn extends Program
{
	website = "https://winworldpc.com/product/fantavision/1x-dos";
	unsafe  = true;
	notes   = "fantavsn PLAYER.EXE loops forever, haven't figured out a way to get it to stop after once. So I record for 40 seconds and that's the result. There is sound, but my dosUtil doesn't support that yet.";
	loc     = "dos";
	bin     = "FANTAVSN/PLAYER.EXE";
	dosData = async r => ({
		timeout  : xu.SECOND*40,
		autoExec : [`COPY ${r.inFile({backslash : true}).toUpperCase()} DOS\\FANTAVSN\\F.MVE`, "CD DOS\\FANTAVSN", "PLAYER.EXE"],
		video    : await r.outFile("out.mp4", {absolute : true})
	});
	renameOut = true;
}
