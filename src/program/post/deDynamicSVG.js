import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil, fileUtil} from "xutil";

export class deDynamicSVG extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	package = ["app-text/xmlstarlet", "net-libs/nodejs"];	// nodejs is for svgo
	unsafe  = true;
	flags   = {
		autoCrop : "Set this flag to also auto crop the SVG using inkscape"
	};
	exec = async r =>
	{
		const RUN_OPTIONS = {timeout : xu.SECOND*30, verbose : r.xlog.atLeast("trace")};

		const outFilePath = await r.outFile("out.svg", {absolute : true});
		await Deno.copyFile(r.inFile({absolute : true}), outFilePath);

		// The <title> and <desc> tags often have 'dynamic' info like current date and time of file generation, let's delete this uselessness so tests run better and labeling can know it's seen the file before
		await runUtil.run("xmlstarlet", ["ed", "--inplace", "-N", "s=http://www.w3.org/2000/svg", "--delete", "/s:svg/s:*[local-name()='desc' or local-name()='title' or local-name()='metadata']", outFilePath], RUN_OPTIONS);

		// A top level 'id' attribute on <svg> serves no real purpose other than to change the hash of the file every time it's generate, so let's get rid of it
		await runUtil.run("xmlstarlet", ["ed", "--inplace", "-N", "s=http://www.w3.org/2000/svg", "--delete", "/s:svg/@id", outFilePath], RUN_OPTIONS);
		
		// WARNING! DO NOT convert this to some sort of 'autoCrop' program beause inkscape only works with 'FileSave' which overrwrites the input file which then isn't detected on output file detection
		if(r.flags.autoCrop)
		{
			const tmpSVGFilePath = await fileUtil.genTempPath(undefined, ".svg");
			
			// OLD: inkscape -g --batch-process --verb FitCanvasToDrawing;FileSave;FileClose outFilePath
			await runUtil.run("inkscape", [`--actions="fit-canvas-to-selection;export-area-drawing;export-filename:${tmpSVGFilePath};export-do`, outFilePath], {virtualX : true, ...RUN_OPTIONS});
			if(await fileUtil.exists(tmpSVGFilePath))
				await fileUtil.move(tmpSVGFilePath, outFilePath);
		}

		//inkscape --actions="fit-canvas-to-selection;export-area-drawing;export-filename:out.svg;export-do" Meeting.svg

		// This will take care of deleting any 'empty' elements
		const {size} = await Deno.lstat(outFilePath);
		if(size<xu.MB*3)	// Don't optimize huge SVG files (like image/svg/grandcan.svg) because it will just run almost forever
			await runUtil.run(Program.binPath("svgo/node_modules/.bin/svgo"), ["--multipass", "--final-newline", outFilePath], RUN_OPTIONS);
	};
	renameOut = true;
}
