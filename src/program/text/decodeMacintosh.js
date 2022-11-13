import {Program} from "../../Program.js";
import {encodeUtil} from "xutil";

export class decodeMacintosh extends Program
{
	website = "https://github.com/Sembiance/deno/blob/master/xutil/encodeUtil.js";
	unsafe  = true;
	flags   = {
		fileEncoding : "The encoding of the data in the input file. Default: utf-8",
		processor    : "Specify the processor to use. Default: percentHex",
		region       : "Specify which region to use for the decoding. Default: roman"
	};
	exec = async r =>
	{
		const inputFileData = new TextDecoder(r.flags.fileEncoding || "utf-8").decode(await Deno.readFile(r.inFile({absolute : true})));
		const decodeOpts = {data : inputFileData, processors : encodeUtil.macintoshProcessors[r.flags.processor || "percentHex"], region : r.flags.region || "roman", preserveWhitespace : true};
		const outputFileData = new TextEncoder("utf-8").encode(await encodeUtil.decodeMacintosh(decodeOpts));
		await Deno.writeFile(await r.outFile(`outfile${r.f.input.ext}`, {absolute : true}), outputFileData);
	};
	renameOut = true;
}
