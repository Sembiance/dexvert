import {Program} from "../../Program.js";
import {initDOMParser, DOMParser} from "denoLandX";
import {dateParse, path} from "std";
import {fileUtil, runUtil, imageUtil} from "xutil";

export class vinetto extends Program
{
	website = "https://github.com/AtesComp/Vinetto";
	package = "app-forensics/vinetto";
	bin     = "vinetto";
	args    = r => ["-o", r.outDir(), "--htmlrep", r.inFile()];
	verify = async (r, dexFile) =>
	{
		if(dexFile.ext===".jpg")
		{
			// sometimes the JPG files output by vinetto are visually all black, but actuall has colors
			// I haven't found a way to expose these colors, but I can detect the all black by converting to PPM and counting colors with that format
			// I filed a bug about it: https://github.com/AtesComp/Vinetto/issues/2
			const tmpPPMFilePath = await fileUtil.genTempPath(undefined, ".ppm");
			await runUtil.run("convert", [dexFile.absolute, tmpPPMFilePath]);
			const imageInfo = await imageUtil.getInfo(tmpPPMFilePath);
			await fileUtil.unlink(tmpPPMFilePath, {recursive : true});
			if(imageInfo && imageInfo.colorCount===1)
				return false;

			return true;
		}

		if(dexFile.ext!==".html")
			return true;

		await initDOMParser();
	
		const doc = new DOMParser().parseFromString(await Deno.readTextFile(dexFile.absolute), "text/html");
		const subs = doc.querySelectorAll("table.sub");
		const filenameMap = {};
		for(const sub of subs)
		{
			const rows = sub.querySelectorAll("tbody tr");
			if(rows.length!==4)
				continue;

			const [, catalogIDRow, filenameRow, catalogInfoRow] = rows;
			const catalogIDs = Array.from(catalogIDRow.querySelectorAll("td.image"), v => v.textContent.trim()).filter(v => !!v);
			const filenames = Array.from(filenameRow.querySelectorAll("td.image"), v => v.textContent.trim()).filter(v => !!v);
			const catalogInfoRegex = /^(?<catalogid>\d+):\s+(?<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\s+Z\s+(?<filename>.+)$/;
			const catalogInfos = catalogInfoRow.querySelector("td:nth-child(2)").textContent.split("\n").filter(v => !!v).map(v => (v.trim().match(catalogInfoRegex) || {groups : {}}).groups).filter(v => !!v);

			if([catalogIDs.length, filenames.length, catalogInfos.length].unique().length!==1)
				continue;

			catalogIDs.forEach((catalogID, i) =>
			{
				const {ts, filename} = catalogInfos.find(({catalogid}) => catalogid===catalogID);
				filenameMap[filenames[i]] = {ts : dateParse(ts, "yyyy-MM-ddTHH:mm:ss")?.getTime(), filename : path.basename(filename.replaceAll("\\", "/"))};	// filename could be an absolute path (windows or unix variety)
			});
		}

		if(Object.keys(filenameMap).length===0)
			return;
		
		r.filenameMap = filenameMap;

		return false;
	};
	post = async r =>
	{
		await Object.entries(r.filenameMap).parallelMap(async ([filename, fileInfo]) =>
		{
			const outputFile = r.f.files.new.find(file => file.base===filename);
			if(!outputFile)
				return;

			await outputFile.rename(fileInfo.filename, {autoRename : true});
			await outputFile.setTS(fileInfo.ts);
		}, 1);	// have to do 1 at a time to avoid race conditions with the autoRename
	};
	renameOut = false;
}
