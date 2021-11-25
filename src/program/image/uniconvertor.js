import {xu} from "xu";
import {Program} from "../../Program.js";

export class uniconvertor extends Program
{
	website       = "https://sk1project.net/uc2/";
	gentooPackage = "media-gfx/uniconvertor";
	gentooOverlay = "dexvert";
	flags         =
	{
		outType : `Which type to convert to (svg || png). Default: svg`
	};

	bin        = "uniconvertor";
	args       = async r => [r.inFile(), await r.outFile(`out.${r.flags.outType || "svg"}`)]
	runOptions = ({timeout : xu.MINUTE*3});
	chain      = r => ((r.flags.outType || "svg")==="svg" ? "deDynamicSVG" : null);
}

/*

exports.runOptions = () => ({timeout : XU.MINUTE*3});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			this.data.outputFilePaths = outputFilePaths;

			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				const finalOutputFilePath = path.join(path.dirname(outputFilePath), path.basename(outputFilePath).replaceAll("outfile", state.input.name));

				// SVG files produced by TotalCADConverter have a border, let's crop it by modifying our viewBox
				if((r.flags.uniconvertorExt || ".svg")===".svg")
					p.util.program.run("deDynamicSVG", {argsd : [outputFilePath, finalOutputFilePath]})(state, p, subcb);
				else
					fileUtil.move(outputFilePath, finalOutputFilePath, subcb);
			}, this);
		},
		function removeOriginals()
		{
			this.data.outputFilePaths.parallelForEach((outputFilePath, subcb) => p.util.file.unlink(outputFilePath)(state, p, subcb), this);
		},
		cb
	);
};
*/
