import {Program} from "../../Program.js";
import {encodeUtil, fileUtil} from "xutil";
import {initDOMParser, DOMParser} from "denoLandX";

export class fixMacJPHTML extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	unsafe  = true;
	exec = async r =>
	{
		await initDOMParser();

		const doc = new DOMParser().parseFromString(await fileUtil.readTextFile(r.inFile({absolute : true})), "text/html");
		
		const imgs = doc.querySelectorAll("img");
		for(const img of imgs)
			img.setAttribute("src", await encodeUtil.decodeMacintosh({data : img.getAttribute("src"), processors : encodeUtil.macintoshProcessors.percentHex, region : "japan"}));

		await Deno.writeTextFile(await r.outFile(`outfile${r.f.input.ext}`, {absolute : true}), doc.querySelector("html").outerHTML);
	};
	renameOut = true;
}
