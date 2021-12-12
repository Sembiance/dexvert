import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";
import {initDOMParser, DOMParser} from "denoLandX";

export class grotag extends Program
{
	website = "http://grotag.sourceforge.net/";
	package = "app-text/grotag";
	bin     = "grotag";

	// Grotag requires absolute paths. Might be due to the way I call the jar file, not sure.
	args    = r => ["-w", r.inFile({absolute : true}), r.outDir({absolute : true})];

	// Grotag can hang at 100% on some guides such as sample bootgauge.guide
	runOptions = ({timeout : xu.MINUTE*2});

	postExec = async r =>
	{
		// grotag creates a seperate CSS file and all HTML files include that. We are gonna inline the CSS into each HTML file and delete the CSS file and move the resulting HTML files up a directory
		const cssFilePath = path.join(r.outDir({absolute : true}), "amigaguide.css");

		const htmlFilePaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true, regex : /\.html$/i});
		if(htmlFilePaths.length===0)
			await fileUtil.unlink(cssFilePath);

		if(!await fileUtil.exists(cssFilePath))
			return;
		
		const cssRaw = await Deno.readTextFile(cssFilePath);

		// The CSS file often has a ton of trailing null bytes, get rid of those. Also all links have this annoying solid gray outline, get rid of that too.
		const cssData = cssRaw.replaceAll("\0", "").trim().replaceAll("outline: solid gray", "");

		await fileUtil.unlink(cssFilePath);

		await initDOMParser();

		await htmlFilePaths.parallelMap(async htmlFilePath =>
		{
			const doc = new DOMParser().parseFromString(await Deno.readTextFile(htmlFilePath), "text/html");

			// Delete any links we have to the external CSS file
			Array.from(doc.querySelectorAll("link")).forEach(o =>
			{
				if((o.getAttribute("href") || "").includes("amigaguide.css"))
					o.remove();
			});

			// Create an inline STYLE tag and insert it into HEAD
			const style = doc.createElement("style");
			style.textContent = cssData;
			doc.querySelector("head").appendChild(style);	// eslint-disable-line unicorn/prefer-dom-node-append

			// Properly encode any hyperlinks (to handle files that have question marks in them, (sample file amigaGuide/FICHEROS))
			Array.from(doc.querySelectorAll("a")).forEach(a => a.setAttribute("href", decodeURIComponent(a.getAttribute("href")).encodeURLPath({skipEncodePercent : true})));

			// For whatever reason, grotag doesn't properly link the Index text to index.html, so we do it ourselves here
			doc.body.insertBefore(doc.createTextNode(" | "), doc.body.childNodes[0]);

			const topLink = doc.createElement("a");
			topLink.setAttribute("href", "index.html");
			topLink.textContent = "Index";
			doc.body.insertBefore(topLink, doc.body.childNodes[0]);

			await Deno.writeTextFile(htmlFilePath, `<html>${doc.head.outerHTML}${doc.body.outerHTML.replaceAll("Contents | Index | ", "")}</html>`);
		});
	};
	renameOut = false;
}
