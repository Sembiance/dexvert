import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {ascii85Decode} from "std";

export class ascii85Decoder extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	unsafe  = true;
	exec    = async r =>
	{
		const outFilePath = await r.outFile("outfile", {absolute : true});
		await Deno.writeFile(outFilePath, ascii85Decode(await fileUtil.readTextFile(r.inFile({absolute : true})), {standard : "btoa"}));
	};
	renameOut = true;
}
