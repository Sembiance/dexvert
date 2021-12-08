import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

export class vcdxrip extends Program
{
	website = "https://www.gnu.org/software/vcdimager";
	package = "media-video/vcdimager";
	unsafe  = true;
	bin     = "vcdxrip";
	args    = r => [`--nofiles`, `--bin-file=${r.inFile({absolute : true})}`];
	cwd     = r => r.outDir();
	postExec = async r =>
	{
		const avseqFilePath = path.join(r.outDir({absolute : true}), "avseq01.mpg");
		
		if(!await fileUtil.exists(avseqFilePath) ||	// we must have this file, or the VCD extraction didn't succeed
			(r.stdout + r.stderr).includes("encountered non-form2 sector -- leaving loop"))	// If the output includes this message then the processing of the VCD failed somewhere and left an incomplete .mpg file
		{
			// so delete whatever was extracted so no files are detected and other converters can try
			await fileUtil.emptyDir(r.outDir({absolute : true}));
			return;
		}

		const videoCDXMLFilePath = path.join(r.outDir({absolute : true}), "videocd.xml");
		if(!await fileUtil.exists(videoCDXMLFilePath))
			return;

		// vcdxrip creates an XML file with a comment with the current command being executed which causes this file to change from run to run due to temp dir, etc.
		// Supposed to be able to pass "--no-command-comment" to vcdxrip to prevent this, but it does not work for me. So we use xmlstarlet to strip out comments
		const {stdout : xmlRaw} = await runUtil.run("xmlstarlet", ["-q", "c14n", "--without-comments", videoCDXMLFilePath]);
		await Deno.writeTextFile(videoCDXMLFilePath, xmlRaw);
	};
	renameOut = false;
}
