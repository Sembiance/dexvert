import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";
import {FileSet} from "../../FileSet.js";

export class vcdxrip extends Program
{
	website = "https://www.gnu.org/software/vcdimager";
	package = "media-video/vcdimager";
	unsafe  = true;
	flags   = {
		reRip : "If set to true, we have an VCD that was ripped incorrectly, so we will virtually mount it with cdemu and re-rip it as BIN/CUE with cdrdao then process those results"
	};
	bin     = "vcdxrip";
	args    = async r =>
	{
		if(!r.flags.reRip)
			return [`--nofiles`, `--bin-file=${r.inFile({absolute : true})}`];

		r.tmpBINCUEDirPath = await fileUtil.genTempPath(undefined, "_vcdxrip_bincue");
		await Deno.mkdir(r.tmpBINCUEDirPath);
		await Program.runProgram("cdemuReRip", await FileSet.create(r.f.root, "input", r.f.input, "outDir", r.tmpBINCUEDirPath), {xlog : r.xlog});
		return [`--nofiles`, `--bin-file=${path.join(r.tmpBINCUEDirPath, "out.bin")}`];
	};
	cwd      = r => r.outDir();
	postExec = async r =>
	{
		const avseqFileCount = (await fileUtil.tree(r.outDir({absolute : true}), {nodir : true, regex : /avseq\d+\.mpg$/})).length;
		const avseqFilePath = path.join(r.outDir({absolute : true}), "avseq01.mpg");
		
		// We used to check for this error: (r.stdout + r.stderr).includes("encountered non-form2 sector -- leaving loop")
		// If it was present, we assumed a complete failure and exited early. But *something* is better than *nothing*
		// This is the case with http://discmaster.textfiles.com/browse/15859
		// So we used to proceed just so long as we have an mpg file that is not empty
		// However then I encountered this one: http://dev.discmaster2.textfiles.com/view/375/VolumeLabel.bin/avseq01.mpg
		// Where it produce just a 120kb file. so now we also check if the file is larger than 5MB when there is only a single avseq result file
		if(!await fileUtil.exists(avseqFilePath) || ((await Deno.stat(avseqFilePath)).size || 0)<(avseqFileCount===1 ? xu.MB*5 : 1))	// If the output includes this message then the processing of the VCD failed somewhere and left an incomplete .mpg file
		{
			if(r.tmpBINCUEDirPath)
				await fileUtil.unlink(r.tmpBINCUEDirPath, {recursive : true});

			// so delete whatever was extracted so no files are detected and other converters can try
			await fileUtil.emptyDir(r.outDir({absolute : true}));
			return;
		}

		// We successfully extracted the video files, but we should also extract the 'regular' files on the disc as well
		await Program.runProgram("fuseiso[excludeVCD]", await FileSet.create(r.f.root, "input", r.tmpBINCUEDirPath ? path.join(r.tmpBINCUEDirPath, "out.bin") : r.f.input, "outDir", r.f.outDir), {xlog : r.xlog});

		if(r.tmpBINCUEDirPath)
			await fileUtil.unlink(r.tmpBINCUEDirPath, {recursive : true});

		const videoCDXMLFilePath = path.join(r.outDir({absolute : true}), "videocd.xml");
		if(!await fileUtil.exists(videoCDXMLFilePath))
			return;

		// vcdxrip creates an XML file with a comment with the current command being executed which causes this file to change from run to run due to temp dir, etc.
		// Supposed to be able to pass "--no-command-comment" to vcdxrip to prevent this, but it does not work for me. So we use xmlstarlet to strip out comments
		const {stdout : xmlRaw} = await runUtil.run("xmlstarlet", ["-q", "c14n", "--without-comments", videoCDXMLFilePath]);
		await fileUtil.writeTextFile(videoCDXMLFilePath, xmlRaw);
	};
	renameOut = false;
}
