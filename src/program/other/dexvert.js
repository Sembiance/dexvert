import {xu} from "xu";
import {Program} from "../../Program.js";

export class dexvert extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags =
	{
		asFormat : "Which format to convert as"
	};

	unsafe = true;
	bin = "/mnt/compendium/.deno/bin/dexvert";
	args = r => [...(r.flags.asFormat ? [`--asFormat=${r.flags.asFormat}`] : []), `--verbose=${xu.verbose}`, r.f.input.rel, r.f.outDir.rel]
}


/*
"

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "dexvert");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) =>
{
	const dexArgs = ["--useTmpOutputDir", "--verbose", state.verbose.toString()];
	if(r.flags.asFormat)
		dexArgs.push("--asFormat", r.flags.asFormat);
	
	dexArgs.push(inPath, outPath);

	return dexArgs;
};

exports.post = (state, p, r, cb) =>
{
	if(r.flags.deleteInput)
		fileUtil.unlink(r.args.at(-2), cb);
	else
		setImmediate(cb);
};
*/
