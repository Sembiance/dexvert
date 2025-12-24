import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";
import {DOMParser} from "/mnt/compendium/DevLab/deno/deno-dom/deno-dom-native.ts";

export class boo2html extends Program
{
	website    = "https://github.com/kev009/boo2pdf";	// NOTE: Despite the name, we produce HTML output and don't convert to PDF
	bin        = Program.binPath("boo2pdf/zulu/bin/java");
	args       = async r => [
		`-Duser.home=${r.f.homeDir.absolute}`,
		"-cp", `${Program.binPath("boo2pdf/bin")}:${Program.binPath("boo2pdf/sys/hlccommon.jar")}:${Program.binPath("boo2pdf/sys/XKS.jar")}`,
		"boo2pdf",
		"-d", path.join(Program.binPath("boo2pdf/sys"), "/"), r.inFile(), await r.outFile("out")
	];
	runOptions = ({virtualX : true, env : {LD_LIBRARY_PATH : Program.binPath("boo2pdf/sys/")}});
	pre = async r =>
	{
		const ibmSCRDirPath = path.join(r.f.homeDir.absolute, ".IBM", "SCR");
		await Deno.mkdir(path.join(ibmSCRDirPath, "cache"), {recursive : true});
		await fileUtil.writeTextFile(path.join(ibmSCRDirPath, "bookmgr.ini"), `IBM Softcopy Reader\nBook Search Path=${ibmSCRDirPath}\nNotes Search Path=${ibmSCRDirPath}/\n`);
	};
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		const outHTMLFilePath = path.join(outDirPath, "out.html");
		let outHTML = await fileUtil.readTextFile(outHTMLFilePath);
		await fileUtil.unlink(outHTMLFilePath);

		// convert our image paths
		for(const filePath of await fileUtil.tree(path.join(r.f.homeDir.absolute, ".IBM", "SCR", "cache"), {nodir : true, depth : 1}))
		{
			if(![".gif", ".jpg", ".png"].some(ext => filePath.endsWith(ext)))	// in bin/boo2pdf/wip/keepRawPictures is modified code that allows these to be saved to disk: ".gdf", ".mmr", ".met"
			{
				r.xlog.warn`SKIPPING OUTPUT FILE: ${filePath}`;
				continue;
			}

			await fileUtil.move(filePath, path.join(outDirPath, path.basename(filePath)));
			outHTML = outHTML.replaceAll(`file:///${filePath}`, path.basename(filePath));
		}

		// convert our anchor links
		const doc = new DOMParser().parseFromString(outHTML, "text/html");
		for(const anchor of doc.querySelectorAll("a"))
		{
			const href = anchor?.getAttribute("href");
			if(!href?.length)
				continue;
			
			if(href.startsWith("MITEM:"))
				anchor.setAttribute("href", `#${href.replace(/^MITEM/, "TOCI")}`);
			else if(href.startsWith("REF:"))
				anchor.setAttribute("href", `#${href.replace(/^REF:/, "")}`);
			else
				anchor.setAttribute("href", `#${href}`);
		}

		// create missing anchors
		for(const iNode of doc.querySelectorAll("i"))
		{
			if(iNode.nextElementSibling?.nodeName?.toLowerCase()!=="b" || !(/[\d.]+/).test(iNode.textContent.trim()))
				continue;

			const anchor = doc.createElement("a");
			anchor.setAttribute("name", `TOCI:${iNode.textContent.trim()}`);
			iNode.parentNode.insertBefore(anchor, iNode);
		}

		const bookHTML = doc.querySelector("html").outerHTML;
		if(!bookHTML || bookHTML.trim().length===0 || bookHTML.trim().toLowerCase()==="<html><head></head><body></body></html>")
			return;

		await fileUtil.writeTextFile(path.join(outDirPath, `${r.originalInput.name}.html`), bookHTML);
	};
	renameOut = false;
}
