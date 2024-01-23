import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";

export class soffice extends Program
{
	website   = "https://www.libreoffice.org";
	package   = "app-office/libreoffice";
	unsafe    = true;
	flags     = {
		format      : "Specify the input file format.",	// https://cgit.freedesktop.org/libreoffice/core/tree/filter/source/config/fragments/filters
		outType     : `Which format to convert into ("svg", "csv", "pdf", "png", etc). Default is "pdf"`,
		autoCropSVG : "If set to true, the output SVG will be autocropped"
	};
	bruteFlags = { image : { outType : "png" } };
	
	bin        = "soffice";
	runOptions = ({virtualX : true});
	exclusive  = "soffice";
	args       = r =>
	{
		const args = [];

		if(["csv", "pdf"].includes(r.flags.outType || "pdf"))
		{
			// So AUTODETECT isn't a real format, but soffice happily ignores it and still honors the subsequent charset
			const format = r.flags.format || "AUTODETECT";
			const isJPYCharset = RUNTIME.globalFlags?.osHint?.macintoshjp || RUNTIME.globalFlags?.osHint?.fmtownsjpy;
			let charset = isJPYCharset ? "CP932" : "CP1252";
			
			// Certain formats require an alternative way to specify the charset: https://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options
			if(["dBase", "Lotus"].includes(format))
				charset = isJPYCharset ? "64" : "1";

			args.push(`--infilter=${format}:${charset}`);
		}
		
		return [...args, "--headless", "--convert-to", (r.flags.outType || "pdf"), "--outdir", r.outDir(), r.inFile()];
	};
	osData    = ({timeout : xu.MINUTE*2});
	chain     = r => (r.flags.outType==="svg" ? `deDynamicSVG${r.flags.autoCropSVG ? "[autoCrop]" : ""}` : null);
	renameOut = true;
}
