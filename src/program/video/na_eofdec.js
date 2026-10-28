import {Program} from "../../Program.js";

export class na_eofdec extends Program
{
	website = "https://nihav.org/eofdec.html";
	package = "media-video/na_eofdec";
	flags   = {
		format  : "Specify which format to treat the input file as. Run `na_eofdec --list-input-formats` for a list. Default: Let the tool decide",
		outType : `Which format to output: avi wav png bmp. Default is avi`
	};
	allowLargeOutput = true;

	bin  = "na_eofdec";
	args = async r =>
	{
		const a = [];
		if(r.flags.format)
			a.push("-ifmt", r.flags.format);
		a.push(r.inFile());
		a.push("-ofmt", ["bmp", "png"].includes(r.flags.outType) ? "imgseq" : (r.flags.outType || "avi"));
		a.push(r.flags.outType==="bmp" ? r.outDir() : await r.outFile(`out.${r.flags.outType==="png" ? "ppm" : (r.flags.outType || "avi")}`));
		return a;
	};
	chain     = r => (r.flags.outType==="wav" ? "sox[type:wav]" : (r.flags.outType==="png" ? "convert" : (r.flags.outType==="bmp" ? "deark[module:bmp]" : "ffmpeg")));
	renameOut = true;
}
