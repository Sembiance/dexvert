import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

export class ffdec extends Program
{
	website = "https://github.com/jindrapetrik/jpexs-decompiler";
	package = "media-gfx/ffdec";
	bin     = "ffdec";
	args    = r => [
		"-cli",
		"-config", "loopMedia=false,parallelSpeedUpThreadCount=20",
		"-exportTimeout", "120",	// Limit export time to 2 minutes. Any longer is likely due to tons of 'dynamic' shapes or large individual frames, don't need to extract all that stuff
		"-select", "1-500",
		"-export", "script,image,shape,morphshape,movie,font,frame,button,sound,binaryData,text", r.outDir(), r.inFile()];
	postExec = async r =>
	{
		// we manually join our frames before Program encounters our output files
		const framesDirPath = path.join(r.outDir({absolute : true}), "frames");
		const frameFilePaths = (await fileUtil.tree(framesDirPath, {nodir : true, regex : /\.png$/i})).map(filePath => path.relative(framesDirPath, filePath)).sortMulti([filePath => (+path.basename(filePath, ".png"))]);

		const {stdout : frameRateRaw} = await runUtil.run("swfdump", ["--rate", r.inFile()], {cwd : r.f.root});
		const frameDelay = (100/(+frameRateRaw.match(/-r (?<rate>\d.+)/)?.groups?.rate));
		const gifFilePath = await r.outFile(`${r.originalInput ? r.originalInput.name : "out"}.gif`, {absolute : true});
		
		await runUtil.run("convert", ["-delay", frameDelay.toString(), "-loop", "0", "-dispose", "previous", ...frameFilePaths, "-strip", gifFilePath], {cwd : framesDirPath});
		await fileUtil.unlink(framesDirPath, {recursive : true});
	};

	// send the output gif to ffmpeg to be turned into an MP4
	chain      = "?ffmpeg";
	chainCheck = (r, chainFile) => chainFile.dir===r.outDir({absolute : true}) && chainFile.ext===".gif";
	renameOut  = false;
}
