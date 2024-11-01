import {xu} from "xu";
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
	runOptions = ({timeout : xu.MINUTE*5, killChildren : true});
	postExec   = async r =>
	{
		// we manually join our frames before Program encounters our output files
		const framesDirPath = path.join(r.outDir({absolute : true}), "frames");
		const frameFilePaths = (await fileUtil.tree(framesDirPath, {nodir : true, regex : /\.png$/i})).map(filePath => path.relative(framesDirPath, filePath)).sortMulti([filePath => (+path.basename(filePath, ".png"))]);

		const swfdumpR = await Program.runProgram("swfdump", r.f.input, {xlog : r.xlog, autoUnlink : true});

		const frameDelay = swfdumpR.meta.frameRate ? (100/swfdumpR.meta.frameRate) : 20;
		const gifFilePath = await r.outFile(`${r.originalInput ? r.originalInput.name : "out"}.gif`, {absolute : true});
		
		await runUtil.run("magick", ["-delay", frameDelay.toString(), "-loop", "0", "-dispose", "previous", ...frameFilePaths, "-strip", gifFilePath], {cwd : framesDirPath});
		await fileUtil.unlink(framesDirPath, {recursive : true});
	};

	verify = (r, dexFile) =>
	{
		const dexFileRel = path.relative(r.outDir({absolute : true}), dexFile.absolute);
		
		// some files like 20001pt1.swf produce huge 900+MB image files. Here we delete any files in the 'images' directory larger than 3x the original file size
		if(dexFileRel.split("/")[0]==="images" && dexFile.size>(r.f.input.size*3))
			return false;

		return true;
	};

	renameOut  = false;

	// send the output gif to ffmpeg to be turned into an MP4
	chain      = "?ffmpeg";
	chainCheck = (r, chainFile) => chainFile.dir===r.outDir({absolute : true}) && chainFile.ext===".gif";
}
