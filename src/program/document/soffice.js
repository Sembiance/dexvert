import {xu} from "xu";
import {Program} from "../../Program.js";

export class soffice extends Program
{
	website = "https://www.libreoffice.org";
	unsafe  = true;
	flags   =
	{
		outType     : `Which format to transform into ("svg", "csv", "pdf", "png", etc). Default is "pdf"`,
		autoCropSVG : "If set to true, the output SVG will be autocropped"
	};
	
	loc      = "gentoo";
	bin      = "soffice";
	args     = r => ["--headless", "--convert-to", (r.flags.outType || "pdf"), "--outdir", "/out", r.inFile()];
	qemuData = () => ({timeout : xu.MINUTE*2});
	chain    = r => ((r.flags.outType || "svg")==="svg" ? `deDynamicSVG${r.flags.autoCropSVG ? "[autoCrop]" : ""}` : null);
}
