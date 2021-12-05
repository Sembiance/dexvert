import {xu} from "xu";
import {Program} from "../../Program.js";

export class irfanView extends Program
{
	website = "https://www.irfanview.com/";
	unsafe  = true;
	loc     = "winxp";
	bin     = "c:\\Program Files\\IrfanView\\i_view32.exe";
	args    = r => [r.inFile(), "/silent", `/convert="c:\\out\\out.png"`];

	// If it doesn't convert in 1 minute, it's not gonna as irfanview often gets stuck in infinite loops with max cpu usage
	qemuData = () => ({timeout : xu.MINUTE});
}
